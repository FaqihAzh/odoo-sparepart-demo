from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductThreshold(models.Model):
    _name = 'product.threshold'
    _description = 'Product Min Max Threshold per Warehouse'
    _rec_name = 'display_name'
    _order = 'product_id, warehouse_id'

    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    min_qty = fields.Float('Min Stock', default=0.0)
    max_qty = fields.Float('Max Stock', default=0.0)

    current_qty = fields.Float('Current Stock', compute='_compute_current_qty', store=False)
    alert_status = fields.Selection([
        ('ok', 'OK'),
        ('under', 'Below Minimum'),
        ('over', 'Above Maximum'),
    ], string='Stock Alert', compute='_compute_alert_status', store=False)

    display_name = fields.Char(string='Display', compute='_compute_display', store=True)

    _sql_constraints = [
        ('product_warehouse_uniq', 'unique(product_id, warehouse_id)', 'Threshold already set for this product and warehouse.'),
    ]

    @api.depends('product_id', 'warehouse_id')
    def _compute_display(self):
        for r in self:
            r.display_name = '%s / %s' % (r.product_id.name or '', r.warehouse_id.name or '')

    @api.constrains('min_qty','max_qty')
    def _check_min_max(self):
        for r in self:
            if r.min_qty < 0 or r.max_qty < 0:
                raise ValidationError(_('Min and Max must be >= 0'))
            if r.max_qty and r.min_qty and r.min_qty > r.max_qty:
                raise ValidationError(_('Min qty cannot be greater than Max qty'))

    @api.depends('product_id','warehouse_id')
    def _compute_current_qty(self):
        """Hitung stock product hanya di warehouse terkait"""
        StockQuant = self.env['stock.quant']
        for r in self:
            if not r.product_id or not r.warehouse_id:
                r.current_qty = 0.0
                continue
            # ambil lokasi internal dari warehouse
            locations = r.warehouse_id.view_location_id.child_ids.filtered(lambda l: l.usage == 'internal')
            qty = 0.0
            for loc in locations:
                quants = StockQuant.read_group(
                    [('product_id', 'in', r.product_id.product_variant_ids.ids),
                     ('location_id', 'child_of', loc.id)],
                    ['quantity:sum'],
                    []
                )
                if quants:
                    qty += quants[0].get('quantity', 0.0)
            r.current_qty = qty

    @api.depends('current_qty','min_qty','max_qty')
    def _compute_alert_status(self):
        for r in self:
            if r.min_qty and r.current_qty < r.min_qty:
                r.alert_status = 'under'
            elif r.max_qty and r.current_qty > r.max_qty:
                r.alert_status = 'over'
            else:
                r.alert_status = 'ok'

    @api.depends('product_id', 'warehouse_id')
    def _compute_current_qty(self):
        """Hitung stock product hanya di warehouse terkait"""
        StockQuant = self.env['stock.quant']
        for r in self:
            if not r.product_id or not r.warehouse_id:
                r.current_qty = 0.0
                continue
            # lokasi internal milik warehouse
            locations = r.warehouse_id.view_location_id.child_ids.filtered(lambda l: l.usage == 'internal')
            qty = 0.0
            for loc in locations:
                quants = StockQuant.read_group(
                    [('product_id', 'in', r.product_id.product_variant_ids.ids),
                     ('location_id', 'child_of', loc.id)],
                    ['quantity:sum'],
                    []
                )
                if quants:
                    qty += quants[0].get('quantity', 0.0)
            r.current_qty = qty
