# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class stock_qr_tracking(models.Model):
#     _name = 'stock_qr_tracking.stock_qr_tracking'
#     _description = 'stock_qr_tracking.stock_qr_tracking'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

