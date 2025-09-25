from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    qr_code = fields.Binary("QR Code", attachment=True)
    qr_code_data = fields.Char("QR Data", compute="_set_qr_data", store=True)
    is_verified = fields.Boolean("Verified", default=False)

    @api.depends("product_id", "picking_id", "lot_id")
    def _set_qr_data(self):
        """Generate data unik untuk QR code"""
        for rec in self:
            if rec.product_id and rec.picking_id:
                rec.qr_code_data = f"{rec.product_id.id}-{rec.picking_id.id}-{rec.id}"
            else:
                rec.qr_code_data = False

    @api.depends("qr_code_data")
    def _generate_qr(self):
        """Generate QR Code binary"""
        for rec in self:
            if rec.qr_code_data:
                qr = qrcode.QRCode(version=1, box_size=3, border=2)
                qr.add_data(rec.qr_code_data)
                qr.make(fit=True)
                img = qr.make_image(fill="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False

    def action_verify_line(self):
        """Tombol verifikasi scan barang"""
        for rec in self:
            rec.is_verified = True

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """Pastikan semua barang sudah di-scan & verified sebelum validasi"""
        for picking in self:
            not_verified = picking.move_line_ids.filtered(lambda l: not l.is_verified)
            if not_verified:
                raise UserError("Tidak bisa validasi, masih ada barang yang belum di-verify dengan scan QR!")
        return super(StockPicking, self).button_validate()
