# -*- coding: utf-8 -*-
# from odoo import http


# class StockQrTracking(http.Controller):
#     @http.route('/stock_qr_tracking/stock_qr_tracking', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_qr_tracking/stock_qr_tracking/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_qr_tracking.listing', {
#             'root': '/stock_qr_tracking/stock_qr_tracking',
#             'objects': http.request.env['stock_qr_tracking.stock_qr_tracking'].search([]),
#         })

#     @http.route('/stock_qr_tracking/stock_qr_tracking/objects/<model("stock_qr_tracking.stock_qr_tracking"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_qr_tracking.object', {
#             'object': obj
#         })

