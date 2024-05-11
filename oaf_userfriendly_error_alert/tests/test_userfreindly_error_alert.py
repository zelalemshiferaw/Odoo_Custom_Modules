from odoo.exceptions import ValidationError,UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

test_pos_order_complete_data = {
  "company_id": 33,
  "date_order": "2024-04-03 11:56:53",
  "etr_state": "draft",
  "name": "Order_Test",
  "partner_id": 22814323,
  "pos_reference": "Order Test",
  "pricelist_id": 367,
  "session_id": 13440,
}

@tagged("post_install")
class TestPOSCreation(TransactionCase):

    def setUp(self):
        super(TestPOSCreation, self).setUp()
        company_id = 33
        order_id = self.env["pos.order"].create({
                      "company_id": 33,
                      "date_order": "2024-04-03 11:56:53",
                      "etr_state": "draft",
                      "name": "Order_Test",
                      "partner_id": 22814323,
                      "pos_reference": "Order Test",
                      "pricelist_id": 367,
                      "session_id": 13440,
                      }
                    )

        product_id = self.env["product.product"].search([('company_id', '=', company_id)], limit=1).id
        if not product_id:
            product_id = self.env["product.product"].create({
                'name': 'Testing_Products',
                'categ_id': self.env['product.category'].search([], limit=1).id,
                'uom_id': self.env['uom.uom'].search([], limit=1).id,
                'uom_po_id': self.env['uom.uom'].search([], limit=1).id,
                'company_id': company_id,
            }).id
        self.env["pos.order.line"].create({
                            "product_id": product_id,
                            "qty": 3,
                            "price_unit": 4,
                            "order_id": order_id.id,
                        })

    # Test for successful POS creation
    def test_create_clients_success(self):
        vals = test_pos_order_complete_data
        pos_order = self.env["pos.order"].create(vals)
        self.assertEqual(pos_order.name, "Order_Test")


    # Test for invalid data types
    def test_create_pos_order_invalid_data_types(self):
        vals = test_pos_order_complete_data
        vals["partner_id"] = "char"
        with self.assertRaises(ValidationError):
            self.env["pos.order"].create(vals)

    # Test for missing required fields
    def test_create_pos_order_missing_required_fields(self):
        vals = {
            "partner_id": 22814323,
            # Missing required fields like session_id
        }
        with self.assertRaises(ValidationError):
            self.env["pos.order"].create(vals)

    # Test for dependency resolution
    def test_create_pos_order_dependency_resolution(self):
        vals = test_pos_order_complete_data
        del vals["partner_id"]  # Missing Partner_id data
        with self.assertRaises(ValidationError):
            self.env["pos.order"].create(vals)


