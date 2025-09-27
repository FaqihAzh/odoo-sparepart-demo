# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CustomerMapController(http.Controller):
    @http.route('/customer_map_tracking/customers_geojson', type='json', auth='user')
    def customers_geojson(self):
        records = request.env['customer.map.tracking'].sudo().search([])
        return [
            {
                'id': rec.id,
                'name': rec.name,
                'address': rec.address or '',
                'geo_point': rec.geo_point and rec.geo_point.geojson and rec.geo_point.geojson['coordinates'] or None,
            }
            for rec in records if rec.geo_point
        ]

    @http.route('/customer_map_tracking/customers', type='json', auth='user')
    def customers_json(self):
        records = request.env['customer.map'].sudo().search([])
        data = []
        for r in records:
            if r.latitude is None or r.longitude is None:
                continue
            data.append({
                'id': r.id,
                'name': r.name,
                'description': r.description or '',
                'phone': r.phone or '',
                'email': r.email or '',
                'latitude': float(r.latitude),
                'longitude': float(r.longitude),
            })
        return data

    @http.route('/customer_map_tracking/customer/<int:rec_id>', type='json', auth='user')
    def customer_single(self, rec_id):
        r = request.env['customer.map'].sudo().browse(rec_id)
        if not r.exists():
            return {'error': 'Not found'}
        return {
            'id': r.id,
            'name': r.name,
            'description': r.description,
            'phone': r.phone,
            'email': r.email,
            'latitude': r.latitude,
            'longitude': r.longitude,
        }
