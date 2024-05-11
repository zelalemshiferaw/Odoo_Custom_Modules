import ast

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

test_sale_order_complete_data = {
    "clientId": "233344",
    "firstName": "John",
    "lastName": "Doe",
    "nid": "xxxx-xxx-xxx",
    "phoneNumber": "+254712341678",
    "channelId": 6,
    "tupande_status": "draft",
    "shopId": 1,
    "orderDate": "2018-02-10T09:30Z",
    "orderRef": "S147561",
    "isCredit": True,
    "amountTotal": 1832.82,
    "orderLines": "[['FURN_1118', 5, 55],['E-COM06', 2, 563],['E-COM01', 2, 563]]",
}
sale_order_data = {"partner_id": 2, "company_id": 1, "so_channel_id": 1, "shop_id": 1}

required_parameters = (
    "clientId",
    "firstName",
    "lastName",
    "nid",
    "orderRef",
    "phoneNumber",
    "orderLines",
    "shopId",
    "channelId",
    "orderDate",
)


@tagged("post_install")
class TestSaleIntegration(TransactionCase):
    def setUp(self):
        super(TestSaleIntegration, self).setUp()
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        order_id = (
            self.env["sale.order"]
            .with_context(is_migrated=True)
            .with_company(company_id)
            .create(
                {
                    "partner_id": self.env["res.partner"].search([], limit=1).id,
                    "so_channel_id": self.env["oaf.channels"].search([], limit=1).id,
                    "shop_id": self.env["res.shop"].search([], limit=1).id,
                    "company_id": company_id,
                }
            )
        )

        product_id = (
            self.env["product.product"]
            .search([("company_id", "=", company_id)], limit=1)
            .id
        ) or (
            self.env["product.product"]
            .create(
                {
                    "name": "Testing_Products",
                    "categ_id": self.env["product.category"].search([], limit=1).id,
                    "uom_id": self.env["uom.uom"].search([], limit=1).id,
                    "uom_po_id": self.env["uom.uom"].search([], limit=1).id,
                    "company_id": company_id,
                }
            )
            .id
        )
        self.env["sale.order.line"].create(
            {
                "product_id": product_id,
                "product_uom_qty": 3,
                "price_unit": 4,
                "order_id": order_id.id,
            }
        )
        order_id.with_context(is_migrated=True).action_confirm()

    # Test for successful client creation

    def test_create_tupande_sale_order_success(self):
        vals = test_sale_order_complete_data
        company_id = False
        product_id = self.env["product.product"]
        order_line_id = self.env["sale.order.line"]
        order_lines_data = ast.literal_eval(vals.get("orderLines"))

        response = self.env["sale.order"].handle_order_tupande(
            sale_order_data,
            order_lines_data,
            company_id,
            vals,
            product_id,
            order_line_id,
        )
        self.assertEqual(response.status_code, 201)

    def test_create_tupande_order_missing_parameters(self):
        vals = {
            "clientId": "233344",
            "firstName": "John",
            "lastName": "Doe",
            "nid": "xxxx-xxx-xxx",
            "phoneNumber": "+250789829182",
            "channelId": 6,
            "tupande_status": "draft",
            "shopId": 1,
            "orderDate": "2018-02-10T09:30Z",
            "amountTotal": 1832.82,
            "orderLines": "[['FURN_1118', 5, 55],"
            "['E-COM06', 2, 563],['E-COM01', 2, 563]]",
        }
        resource = self.env["sale.order"].any_parameter_missing(
            required_parameters, vals
        )
        self.assertEqual(resource.status_code, 400)
        self.assertEqual(resource.status, "400 BAD REQUEST")
