import base64
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class FSMApiController(http.Controller):
    """
    Simple REST endpoints for mobile technicians:
      - /api/auth/login  (json) -> login and create session
      - /api/fsm_orders   (json, auth='user') -> list orders assigned to current user
      - /api/fsm_orders/<id>/update (json, auth='user') -> update fields, checklist, upload photo
    """

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **post):
        """
        Request JSON: { "db": "mydb", "login": "tech1", "password": "pass" }
        Response: { "uid": <uid>, "db": "mydb", "session_id": "<session>" , "user": { ... } }
        """
        db = post.get('db') or request.env.cr.dbname
        login = post.get('login')
        password = post.get('password')

        if not login or not password:
            return {"error": "login and password required"}

        try:
            # authenticate sets session credentials
            request.session.authenticate(db, login, password)
            uid = request.session.uid
            user = request.env['res.users'].sudo().browse(uid).read(['id','name','login'])[0]
            return {
                "uid": uid,
                "db": db,
                "session_id": request.session.sid,
                "user": user
            }
        except Exception as e:
            _logger.exception("Login failed")
            return {"error": "Authentication failed: %s" % (str(e),)}

    @http.route('/api/fsm_orders', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_fsm_orders(self, **post):
        """
        Body (optional JSON):
          {
            "state": ["assigned","in_progress"],   # optional state filter
            "limit": 50
          }
        Returns list of fsm.order for current user (assigned to him).
        """
        uid = request.session.uid
        params = post or {}
        state_filter = params.get('state')
        limit = params.get('limit', 100)

        # find common assigned field name on fsm.order
        fsm = request.env['fsm.order'].sudo()
        # possible fields linking to user: 'user_id','assigned_user_id','technician_id'
        user_field = None
        for f in ['user_id', 'assigned_user_id', 'technician_id', 'worker_id']:
            if f in fsm._fields:
                user_field = f
                break

        domain = []
        if user_field:
            domain.append((user_field, '=', uid))
        # apply state filter if provided
        if state_filter:
            if isinstance(state_filter, (list, tuple)):
                domain.append(('state', 'in', state_filter))
            else:
                domain.append(('state', '=', state_filter))
        # orders = fsm.search_read(domain, ['id','name','install_lat','install_lon','state','scheduled_date'], limit=limit)
        orders = fsm.search_read(
            domain,
            ['id', 'name', 'location_id','install_lat','install_lon',
             'stage_id', 'scheduled_date_start'],
            limit=limit
        )
        return {'orders': orders}

    @http.route('/api/fsm_orders/<int:order_id>/update', type='json', auth='user', methods=['POST'], csrf=False)
    def api_update_fsm_order(self, order_id, **post):
        """
        Update FSM order fields, checklist, and optionally upload image.
        JSON payload sample:
        {
          "install_lat": -6.200000,
          "install_lon": 106.816666,
          "state": "done",
          "checklist": [
            {"id": 12, "is_done": true},
            {"id": null, "name": "Grounding checked", "is_done": true}
          ],
          "attachments": [
            {"name":"photo1.jpg", "mimetype":"image/jpeg", "content_base64":"..."}
          ]
        }
        """
        user = request.env.user
        order = request.env['fsm.order'].sudo().browse(order_id)
        if not order.exists():
            return {"error": "Order not found"}

        vals = {}
        if 'install_lat' in post:
            vals['install_lat'] = post.get('install_lat')
        if 'install_lon' in post:
            vals['install_lon'] = post.get('install_lon')
        # try to write state; actual field name might be 'state' or 'stage_id' - we attempt both
        if 'state' in post and 'state' in order._fields:
            vals['state'] = post.get('state')
        elif 'state' in post and 'stage_id' in order._fields:
            # user passed a stage name or id; if id provided, write directly, otherwise try to find stage by name
            st = post.get('state')
            try:
                st_id = int(st)
                vals['stage_id'] = st_id
            except Exception:
                stage = request.env['fsm.stage'].sudo().search([('name','ilike', st)], limit=1)
                if stage:
                    vals['stage_id'] = stage.id

        # write main vals if any
        if vals:
            order.sudo().write(vals)

        # handle checklist items
        checklist_items = post.get('checklist') or []
        for cl in checklist_items:
            cl_id = cl.get('id')
            if cl_id:
                try:
                    rec = request.env['installation.checklist'].sudo().browse(int(cl_id))
                    write_vals = {}
                    if 'is_done' in cl:
                        write_vals['is_done'] = bool(cl.get('is_done'))
                        if write_vals['is_done']:
                            write_vals['done_by'] = user.id
                    if 'name' in cl:
                        write_vals['name'] = cl.get('name')
                    if write_vals:
                        rec.sudo().write(write_vals)
                except Exception:
                    _logger.exception("Failed to update checklist id %s", cl_id)
            else:
                # create new checklist row
                create_vals = {
                    'fsm_order_id': order.id,
                    'name': cl.get('name') or 'Checklist item',
                    'is_done': bool(cl.get('is_done', False)),
                    'done_by': user.id if cl.get('is_done') else False
                }
                request.env['installation.checklist'].sudo().create(create_vals)

        # handle attachments (array of {name, content_base64, mimetype})
        attachments = post.get('attachments') or []
        for att in attachments:
            try:
                data = att.get('content_base64')
                if not data:
                    continue
                fname = att.get('name', 'file.bin')
                mimetype = att.get('mimetype', 'application/octet-stream')
                request.env['ir.attachment'].sudo().create({
                    'name': fname,
                    'type': 'binary',
                    'mimetype': mimetype,
                    'datas': data,
                    'res_model': 'fsm.order',
                    'res_id': order.id,
                    'public': False,
                })
            except Exception:
                _logger.exception("Failed to create attachment for order %s", order.id)

        return {"success": True, "order_id": order.id}
