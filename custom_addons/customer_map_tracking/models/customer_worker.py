from odoo import models, fields, api

class CustomerWorker(models.Model):
    _name = "customer.worker"
    _description = "Customer / Worker with map location"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    partner_id = fields.Many2one('res.partner', string='Partner')
    is_worker = fields.Boolean(string='Is Worker', default=False)

    lat = fields.Float(string="Latitude", digits=(16, 6))
    lon = fields.Float(string="Longitude", digits=(16, 6))

    image = fields.Binary("Image", attachment=True)

    def action_open_map_picker(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'customer_map_tracking.map_action',
            'target': 'new',
            'context': {'active_id': self.id, 'map_picker': True}
        }
