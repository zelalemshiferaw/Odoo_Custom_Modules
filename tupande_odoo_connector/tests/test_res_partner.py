import random

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

test_partner_complete_data = {
    "id": "11111",
    "firstName": "John",
    "lastName": "Doe",
    "verified": "false",
    "nid": "12345678",
    "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
    "phoneNumber": "254712345678",
}
test_partner_wrong_phone_number = {
    "id": "22222",
    "firstName": "John",
    "lastName": "Doe",
    "verified": "false",
    "nid": "12345609",
    "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
    "phoneNumber": "++25479898912345678",
}

test_partner_parameter_missing = {
    "id": "33333",
    "lastName": "Doe",
    "verified": "false",
    "nid": "12349876",
    "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
    "phoneNumber": "++25479898912345678",
}
test_partner_invalid_nid = {
    "id": "33336",
    "lastName": "Doe",
    "verified": "false",
    "nid": "111",
    "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
    "phoneNumber": "+254798989123",
}
test_multi_partner_complete_data = [
    {
        "id": "999999",
        "firstName": "Usman",
        "lastName": "Akbar",
        "verified": "false",
        "nid": "222-xxx-xxx",
        "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
        "phoneNumber": "+254712145078",
    },
    {
        "id": "10101010",
        "firstName": "Ali",
        "lastName": "Ahmad",
        "verified": "false",
        "nid": "xxxx-333-xxx",
        "picture": "https://avatars.githubusercontent.com/u/43511880?s=60&v=4",
        "phoneNumber": "+254702345679",
    },
]


@tagged("-at_install", "post_install")
class TestIntegration(TransactionCase):
    def setUp(self):
        super().setUp()
        vals = {
            "id": "200004",
            "firstName": "John",
            "lastName": "Doing",
            "gender": "Male",
            "verified": "false",
            "phoneNumber": "254719411295",
        }
        self.env["res.partner"].create(vals)
        self.assertEqual(self.partner.firstname, "John")

    # Test for successful client creation
    def test_create_tupande_clients_success(self):
        vals = test_partner_complete_data
        vals["id"] = 12345
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        response = self.env["res.partner"].handle_client_info(
            vals, res_partner, country_id, company_id
        )
        self.assertEqual(response.get("id"), 12345)

    def test_create_tupande_clients_phone_number_missing(self):
        vals = {
            "id": "222",
            "firstName": "John",
            "lastName": "Doe",
            "verified": "false",
            "nid": "xxxx-xxx-xxx",
            "picture": "https://avatars.githubusercontent.com/u/45451919?v=4",
        }
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        response = self.env["res.partner"].handle_client_info(
            vals, res_partner, country_id, company_id
        )
        self.assertEqual(
            response.get("message"),
            "You didn't update First Name or "
            "Second Name or tupande ID or Phone Number",
        )

    # Test for multipul successful client creation
    def test_updated_multiple_tupande_clients_success(self):
        vals = test_multi_partner_complete_data
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        responses = [
            self.env["res.partner"].handle_client_info(
                client, res_partner, country_id, company_id
            )
            for client in vals
        ]
        for response in responses:
            self.assertEqual(response.get("httpStatusCode"), "201")

    def generate_six_digit_number(self):
        return random.randint(100000, 999999)

    def test_update_tupande_clients_success(self):
        random_digits = self.generate_six_digit_number()
        vals = {
            "id": f"{random_digits}",
            "firstName": "Perte",
            "lastName": "Doe",
            "gender": "Male",
            "verified": "false",
            "phoneNumber": f"254719{random_digits}",
        }
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        new_partner = self.env["res.partner"].handle_client_info(
            vals, res_partner, country_id, company_id
        )
        self.assertEqual(new_partner.httpStatusCode, "201")
        # Update the client name
        vals["firstName"] = "Client Updated"
        updated_new_partner = self.env["res.partner"].handle_client_info(
            vals, res_partner, country_id, company_id, vals["id"]
        )
        self.assertEqual(updated_new_partner.httpStatusCode, "200")

    def test_create_tupande_client_invalid_nid(self):
        random_digits = self.generate_six_digit_number()
        vals = test_partner_invalid_nid
        vals["id"] = f"{random_digits}"
        vals["phoneNumber"] = f"254719{random_digits}"
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        resource = self.env["res.partner"].handle_client_info(
            vals, res_partner, country_id, company_id
        )
        self.assertEqual(
            resource.get("message"),
            "The NID provided is not valid",
        )

    def test_create_or_update_tupande_clients_missing_required_fields(self):
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        resource = self.env["res.partner"].handle_client_info(
            test_partner_parameter_missing, res_partner, country_id, company_id
        )
        self.assertEqual(
            resource.get("message"),
            "You didn't update First Name "
            "or Second Name or tupande ID or Phone Number",
        )

    def test_validation_tupande_clients_wrong_phone_number(self):
        company_id = self.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        country_id = self.env.ref("base.ke").id
        res_partner = self.env["res.partner"].sudo()
        resource = self.env["res.partner"].handle_client_info(
            test_partner_wrong_phone_number, res_partner, country_id, company_id
        )
        self.assertEqual(
            resource.get("message"), "Your phone number didn't match with right pattern"
        )
