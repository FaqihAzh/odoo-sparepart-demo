from odoo import models, fields


class CustomerDetailWizard(models.TransientModel):
    _name = 'customer.detail.wizard'
    _description = 'Customer Detail Modal'

    customer_id = fields.Many2one('customer.worker', string='Customer', required=True)
    name = fields.Char(related='customer_id.name', readonly=True)
    description = fields.Text(related='customer_id.description', readonly=True)
    email = fields.Char(related='customer_id.email', readonly=True)
    phone = fields.Char(related='customer_id.phone', readonly=True)
    latitude = fields.Float(related='customer_id.latitude', readonly=True)
    longitude = fields.Float(related='customer_id.longitude', readonly=True)
