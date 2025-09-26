from odoo import models, fields


class CustomerWorker(models.Model):
    _name = 'customer.worker'
    _description = 'Customer / Worker'
    _order = 'name'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    latitude = fields.Float('Latitude', digits=(16, 6))
    longitude = fields.Float('Longitude', digits=(16, 6))
