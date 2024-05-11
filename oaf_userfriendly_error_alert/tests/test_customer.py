from odoo.exceptions import ValidationError,UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

test_partner_complete_data = {
    "name":"Test Client",
    "firstName": "John",
    "lastName": "Doe",
    "nid": "xxxx-111-xxx",
    "phoneNumber": "+254712345678"
  }

@tagged("post_install")
class TestClientCreation(TransactionCase):

    def setUp(self):
        super(TestClient, self).setUp()
        vals = {"name": "Test Client"}
        self.test_partner = self.env["res.partner"].create(vals)

    # Test for successful client creation
    def test_create_clients_success(self):
        vals = test_partner_complete_data
        partner = self.env["res.partner"].create(vals)
        self.assertEqual(partner.name, "Test Client")

    # Test for invalid data types
    def test_create_clients_invalid_data_types(self):
        vals = {
            "name": 1,  # Invalid Name type
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)

    # Test for missing required fields
    def test_create_clients_missing_required_fields(self):
        vals = {
            "function": "sales",
            # Missing required fields like name
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)

