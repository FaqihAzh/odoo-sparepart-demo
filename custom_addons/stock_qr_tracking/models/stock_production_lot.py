from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import uuid

try:
    import qrcode
    from PIL import Image
except Exception:
    qrcode = None

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    qr_string = fields.Char(string="QR String", copy=False, index=True)
    qr_image = fields.Binary(string="QR Image", attachment=True, copy=False)
    purchase_id = fields.Many2one('purchase.order', string='Source PO', copy=False)
    purchase_date = fields.Datetime(string='Purchase Date', copy=False)
    supplier_id = fields.Many2one('res.partner', string='Supplier', copy=False)
    purchase_name = fields.Char(string='Purchase Name', copy=False)  # PO name / invoice no
    sales_ref = fields.Char(string='Sales Ref', copy=False)          # optional: sales invoice/ref
    customer_name = fields.Char(string='Customer Name', copy=False)  # optional
    status = fields.Selection([
        ('label_created','Label Created'),
        ('sticker_attached','Sticker Attached'),
        ('received','Received'),
        ('sold','Sold'),
        ('returned','Returned'),
    ], string='Status', default='label_created', copy=False)

    _sql_constraints = [
        ('qr_string_uniq', 'unique(qr_string)', 'QR string must be unique.')
    ]

    def generate_qr_image(self, content):
        """Return base64 PNG image for QR code (requires qrcode + Pillow)."""
        if qrcode is None:
            raise UserError(_("Library qrcode/Pillow belum terinstall. Jalankan: pip install qrcode pillow"))
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())
