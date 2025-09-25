from odoo import models, fields, api, _
import uuid

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    qr_generated = fields.Boolean(string="QR Generated", default=False, copy=False)

    def action_generate_qr(self):
        """Generate per-unit QR lots for all lines that have qr_enabled product."""
        Lot = self.env['stock.production.lot'].sudo()
        for po in self:
            if po.qr_generated:
                continue
            for line in po.order_line:
                product = line.product_id
                # only for products enabled for QR tracking
                try:
                    qr_enabled = product.product_tmpl_id.qr_enabled
                except Exception:
                    qr_enabled = getattr(product, 'qr_enabled', False)
                if not qr_enabled:
                    continue
                qty = int(line.product_qty)
                for i in range(qty):
                    qr_code = f"{po.name}-{product.default_code or product.id}-{uuid.uuid4().hex[:8]}"
                    vals = {
                        'name': qr_code,
                        'qr_string': qr_code,
                        'product_id': product.id,
                        'purchase_id': po.id,
                        'purchase_date': po.date_order or fields.Datetime.now(),
                        'supplier_id': po.partner_id.id,
                        'purchase_name': po.name,
                    }
                    lot = Lot.create(vals)
                    # generate image
                    try:
                        lot.sudo().write({'qr_image': lot.generate_qr_image(qr_code)})
                    except Exception:
                        # ignore image generation errors but keep lot
                        pass
            po.qr_generated = True
        return True

    def action_print_qr_labels(self):
        # action to call QWeb report for this PO
        return self.env.ref('stock_qr_tracking.report_purchase_qr_action').report_action(self)

    def _get_lots(self):
        Lot = self.env['stock.production.lot']
        return Lot.search([('purchase_id','=', self.id)])
