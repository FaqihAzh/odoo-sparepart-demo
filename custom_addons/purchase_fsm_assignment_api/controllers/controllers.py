# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseFsmAssignmentApi(http.Controller):
#     @http.route('/purchase_fsm_assignment_api/purchase_fsm_assignment_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_fsm_assignment_api/purchase_fsm_assignment_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_fsm_assignment_api.listing', {
#             'root': '/purchase_fsm_assignment_api/purchase_fsm_assignment_api',
#             'objects': http.request.env['purchase_fsm_assignment_api.purchase_fsm_assignment_api'].search([]),
#         })

#     @http.route('/purchase_fsm_assignment_api/purchase_fsm_assignment_api/objects/<model("purchase_fsm_assignment_api.purchase_fsm_assignment_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_fsm_assignment_api.object', {
#             'object': obj
#         })

