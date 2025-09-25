# stock_qr_tracking/controllers/qr_controller.py
from odoo import http
from odoo.http import request

class QRController(http.Controller):

    @http.route('/stock_qr/scan', type='json', auth='user', methods=['POST'])
    def scan_qr(self, qr_string=None, picking_id=None):
        """Scan QR endpoint. Called by barcode teams (browser/device).
        Payload: { "qr_string": "PO0001-P123-abc123", "picking_id": 45 }
        """
        if not qr_string or not picking_id:
            return {'error': True, 'message': 'Missing qr_string or picking_id'}

        Lot = request.env['stock.production.lot'].sudo()
        lot = Lot.search([('qr_string','=',qr_string)], limit=1)
        if not lot:
            return {'error': True, 'message': 'QR not found'}

        picking = request.env['stock.picking'].sudo().browse(int(picking_id))
        if not picking.exists():
            return {'error': True, 'message': 'Picking not found'}

        # find move which matches product and still needs qty (move without enough qty_done)
        move = None
        for m in picking.move_ids_without_package:
            if m.product_id.id == lot.product_id.id:
                done = sum(picking.move_line_ids.filtered(lambda ml: ml.product_id.id == m.product_id.id).mapped('qty_done')) if picking.move_line_ids else 0.0
                if done < m.product_uom_qty:
                    move = m
                    break

        MoveLine = request.env['stock.move.line'].sudo()
        if move:
            # try to update existing move_line without lot
            ml = picking.move_line_ids.filtered(lambda x: x.product_id.id == lot.product_id.id and (not x.lot_id or x.qty_done < x.product_uom_qty))
            if ml:
                target = ml[0]
                new_qty = (target.qty_done or 0.0) + 1.0
                target.sudo().write({'lot_id': lot.id, 'qty_done': new_qty})
            else:
                MoveLine.create({
                    'picking_id': picking.id,
                    'product_id': lot.product_id.id,
                    'product_uom_id': lot.product_id.uom_id.id,
                    'lot_id': lot.id,
                    'qty_done': 1.0,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                })
        else:
            # fallback: create new move_line
            MoveLine.create({
                'picking_id': picking.id,
                'product_id': lot.product_id.id,
                'product_uom_id': lot.product_id.uom_id.id,
                'lot_id': lot.id,
                'qty_done': 1.0,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })

        # mark lot status sticker_attached or received
        lot.sudo().write({'status': 'sticker_attached'})

        # if all done -> validate picking
        all_done = True
        for m in picking.move_ids_without_package:
            done = sum(picking.move_line_ids.filtered(lambda ml: ml.product_id==m.product_id).mapped('qty_done')) if picking.move_line_ids else 0.0
            if done < m.product_uom_qty:
                all_done = False
                break

        if all_done:
            try:
                picking.sudo().button_validate()
                # mark lots as received
                for ml in picking.move_line_ids:
                    if ml.lot_id:
                        ml.lot_id.sudo().write({'status': 'received'})
            except Exception as e:
                # couldn't auto-validate: return info
                return {'error': False, 'message': 'Scanned OK, picking ready for manual validation', 'lot_id': lot.id}

        return {'error': False, 'message': 'Scanned OK', 'lot_id': lot.id}
