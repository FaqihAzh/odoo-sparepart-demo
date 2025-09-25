from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    active = fields.Boolean('Active', default=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    item_code = fields.Char(string='Item Code', copy=False, readonly=True, index=True)
    brand_id = fields.Many2one('product.brand', string='Brand')
    default_supplier_id = fields.Many2one('res.partner', string='Default Supplier', domain="[('supplier_rank','>',0)]")
    qr_enabled = fields.Boolean(string='Enable QR Tracking', default=False, help='Jika aktif, product ini akan di-generate QR per unit pada proses penerimaan/purchase.')
    # Reuse existing image_1920 field for product photo (Odoo core). If needed, alias:
    image = fields.Binary(related='image_1920', string='Product Image', readonly=False)

    # for quick min/max update convenience: one2many to threshold lines
    threshold_ids = fields.One2many('product.threshold', 'product_id', string='Min/Max Thresholds')

    _sql_constraints = [
        ('item_code_uniq', 'unique(item_code)', 'Item Code must be unique.'),
        ('name_uniq', 'unique(name)', 'Product name must be unique.'),
    ]

    @api.model
    def create(self, vals):
        # Auto-generate item_code if not provided
        if not vals.get('item_code'):
            seq = self.env['ir.sequence'].sudo().search([('code','=','product.master.item.code')], limit=1)
            if not seq:
                # fallback: use generic sequence via next_by_code
                try:
                    vals['item_code'] = self.env['ir.sequence'].sudo().next_by_code('product.master.item.code') or False
                except Exception:
                    vals['item_code'] = False
            else:
                vals['item_code'] = self.env['ir.sequence'].sudo().next_by_code('product.master.item.code')
        rec = super(ProductTemplate, self).create(vals)
        return rec

    def write(self, vals):
        # Prevent changing item_code to a value that duplicates existing
        if vals.get('item_code'):
            existing = self.search([('item_code','=', vals.get('item_code')), ('id','not in', self.ids)])
            if existing:
                raise UserError(_('Item Code %s already exists.') % vals.get('item_code'))
        if vals.get('name'):
            existing2 = self.search([('name','=', vals.get('name')), ('id','not in', self.ids)])
            if existing2:
                raise UserError(_('Product name %s already exists.') % vals.get('name'))
        return super(ProductTemplate, self).write(vals)

    def quick_update_minmax(self, warehouse_id, min_qty=None, max_qty=None):
        """Helper to quickly update (or create) threshold for given warehouse for these products."""
        Threshold = self.env['product.threshold']
        for product in self:
            thr = Threshold.search([('product_id','=',product.id),('warehouse_id','=',warehouse_id)], limit=1)
            vals = {}
            if min_qty is not None:
                vals['min_qty'] = min_qty
            if max_qty is not None:
                vals['max_qty'] = max_qty
            if thr:
                thr.write(vals)
            else:
                vals.update({'product_id': product.id, 'warehouse_id': warehouse_id})
                Threshold.create(vals)
        return True
