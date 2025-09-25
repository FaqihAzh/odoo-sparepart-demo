# -*- coding: utf-8 -*-
# from odoo import http


# class ProductMaster(http.Controller):
#     @http.route('/product_master/product_master', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_master/product_master/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_master.listing', {
#             'root': '/product_master/product_master',
#             'objects': http.request.env['product_master.product_master'].search([]),
#         })

#     @http.route('/product_master/product_master/objects/<model("product_master.product_master"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_master.object', {
#             'object': obj
#         })

