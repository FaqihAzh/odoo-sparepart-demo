# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class product_master(models.Model):
#     _name = 'product_master.product_master'
#     _description = 'product_master.product_master'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

