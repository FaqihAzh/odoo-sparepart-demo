from odoo import models, fields

class FSMOrderInherit(models.Model):
    _inherit = "fsm.order"

    # Simple lat/lon to record installation point if GeoEngine is not available.
    install_lat = fields.Float(string="Install Latitude")
    install_lon = fields.Float(string="Install Longitude")

    # one2many to pickings for convenience
    picking_ids = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='fsm_order_id',
        string='Related Pickings'
    )

    # one2many to checklist lines
    installation_checklist_ids = fields.One2many(
        comodel_name='installation.checklist',
        inverse_name='fsm_order_id',
        string='Installation Checklist'
    )
