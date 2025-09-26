from odoo import http
from odoo.http import request


class CustomerMapController(http.Controller):

    # 1. Menyajikan halaman dashboard (opsional, kalau Anda pakai QWeb)
    @http.route('/customer_map_tracking/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kw):
        return request.render('customer_map_tracking.dashboard_template', {})

    # 2. Endpoint data JSON untuk peta
    @http.route('/customer_map_tracking/data', type='json', auth='user')
    def data(self, **kw):
        customers = request.env['customer.worker'].search([])   # sudo() hapus jika tidak perlu
        result = []
        for c in customers:
            try:
                lat = float(c.latitude) if c.latitude else None
                lng = float(c.longitude) if c.longitude else None
            except (TypeError, ValueError):
                lat = lng = None
            if lat is not None and lng is not None:
                result.append({
                    'id': c.id,
                    'name': c.name,
                    'latitude': lat,
                    'longitude': lng,
                    'email': c.email or '',
                    'phone': c.phone or '',
                    'description': c.description or '',
                })
        return result

    # 3. Detail single customer (pop-up)
    @http.route('/customer_map_tracking/get/<int:customer_id>', type='json', auth='user')
    def get_customer(self, customer_id, **kw):
        c = request.env['customer.worker'].browse(customer_id)  # sudo() kalau perlu
        if not c.exists():
            return {'error': 'Not found'}
        return {
            'id': c.id,
            'name': c.name or '',
            'description': c.description or '',
            'email': c.email or '',
            'phone': c.phone or '',
            'latitude': float(c.latitude) if c.latitude else None,
            'longitude': float(c.longitude) if c.longitude else None,
        }