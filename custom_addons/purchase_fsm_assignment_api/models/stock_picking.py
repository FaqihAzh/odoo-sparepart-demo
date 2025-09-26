from odoo import models, fields

class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Installation Order",
        help="Link to Field Service installation order"
    )
