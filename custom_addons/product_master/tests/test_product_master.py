from odoo.tests.common import TransactionCase

class TestProductMaster(TransactionCase):

    def setUp(self):
        super().setUp()
        self.brand = self.env['product.brand'].create({'name': 'T-Brand'})
        partner = self.env['res.partner'].create({'name': 'Supp Test', 'supplier_rank':1})
        self.product = self.env['product.template'].create({
            'name': 'PM Test Product',
            'brand_id': self.brand.id,
            'default_supplier_id': partner.id,
            'type': 'product',
        })

    def test_item_code_generated(self):
        self.assertTrue(self.product.item_code, "Item code should be auto generated")

    def test_quick_update_threshold(self):
        wh = self.env['stock.warehouse'].search([], limit=1)
        if not wh:
            wh = self.env['stock.warehouse'].create({'name':'WH Test', 'code':'WHT'})
        self.product.quick_update_minmax(wh.id, min_qty=5, max_qty=20)
        thr = self.env['product.threshold'].search([('product_id','=',self.product.id), ('warehouse_id','=',wh.id)], limit=1)
        self.assertTrue(thr, "threshold should be created")
        self.assertEqual(thr.min_qty, 5)
        self.assertEqual(thr.max_qty, 20)
