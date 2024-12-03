# -*- coding: utf-8 -*-

import base64
import logging
import re
from datetime import datetime

import requests
from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    tupande_client_id = fields.Char(string="Tupande ID")
    age = fields.Selection(
        selection=[
            ("18 - 25", "18 - 25"),
            ("26 - 30", "26 - 30"),
            ("31 - 35", "31 - 35"),
            ("36 - 40", "36 - 40"),
            ("41 - 50", "41 - 50"),
            ("51 - 60", "51 - 60"),
            ("Above 60", "Above 60"),
        ],
        string="Age",
    )

    def check_validation_or_return_gender_and_picture(self, customer, client_id):
        if not client_id and (
            not customer.get("firstName")
            or not customer.get("lastName")
            or not customer.get("id")
            or not customer.get("phoneNumber")
        ):
            return {
                "httpStatusCode": "400",
                "id": customer.get("id"),
                "odoo-id": False,
                "parameterName": "firstName or lastName or ID",
                "message": "You didn't update "
                "First Name or "
                "Second Name or "
                "tupande ID or Phone Number",
            }

        if customer.get("phoneNumber") and not re.match(
            r"(0|\+?254)7\d{8}", customer.get("phoneNumber")
        ):
            return {
                "httpStatusCode": "400",
                "id": customer.get("id"),
                "odoo-id": False,
                "parameterName": "phone",
                "message": "Your phone number didn't match with right pattern",
            }

        gender = False
        picture = False
        if customer.get("gender") == "Male":
            gender = self.env.ref("ce_portal.male").id
        elif customer.get("gender") == "Female":
            gender = self.env.ref("ce_portal.female").id

        if customer.get("picture"):
            get_image = requests.get(customer.get("picture"))
            picture = (
                base64.b64encode(get_image.content)
                if get_image.status_code == 200
                else False
            )
        return [gender, picture]

    def get_update_data(
        self, customer, partner_tupande_id, gender, picture, country_id, company_id
    ):
        return {
            "tupande_client_id": customer.get("id")
            if customer.get("id")
            else partner_tupande_id.tupande_client_id,
            "firstname": customer.get("firstName")
            if customer.get("firstName")
            else partner_tupande_id.firstname,
            "lastname": customer.get("lastName")
            if customer.get("lastName")
            else partner_tupande_id.lastName,
            "gender_id": gender if gender else partner_tupande_id.gender_id,
            "contact_type": "contact",
            "image_1920": picture if picture else partner_tupande_id.image_1920,
            "credit_client": True,
            "nid": customer.get("nid")
            if customer.get("nid")
            else partner_tupande_id.nid,
            "date_of_birth": customer.get("dob")
            if customer.get("dob")
            else partner_tupande_id.date_of_birth,
            "country_id": country_id
            if country_id
            else partner_tupande_id.country_id.id,
            "company_id": company_id
            if company_id
            else partner_tupande_id.company_id.id,
            "age": customer.get("age")
            if customer.get("age")
            else partner_tupande_id.age,
            "phone": customer.get("phoneNumber")
            if customer.get("phoneNumber")
            else partner_tupande_id.phone,
        }

    def get_create_data(self, customer, gender, picture, country_id, company_id):
        return {
            "tupande_client_id": customer.get("id"),
            "firstname": customer.get("firstName"),
            "lastname": customer.get("lastName"),
            "gender_id": gender,
            "image_1920": picture,
            "activation_date": str(datetime.now().date()),
            "nid": customer.get("nid"),
            "contact_type": "contact",
            "state": "inactive",
            "credit_client": True,
            "country_id": country_id,
            "company_id": company_id,
            "phone": customer.get("phoneNumber"),
            "date_of_birth": customer.get("dob"),
            "age": customer.get("age"),
        }

    def handle_client_info(
        self,
        customer,
        res_partner,
        country_id,
        company_id,
        client_id=False,
    ):
        response = self.check_validation_or_return_gender_and_picture(
            customer, client_id
        )
        if not client_id and isinstance(response, dict):
            return response

        gender = response[0]
        picture = response[1]

        customer["phoneNumber"] = res_partner.phone_format(
            customer["phoneNumber"], self.env.ref("base.ke")
        )
        partner_phone_id = self.get_partner_phone_id(customer, res_partner)
        partner_tupande_id = self.get_partner_tupande_id(customer, res_partner)
        phone_number_message = self.get_phone_number_message(customer)
        verify_client_id = self.verify_client_id(client_id, res_partner)
        verify_client_nid = self.verify_client_nid(customer, res_partner)
        if not isinstance(verify_client_nid, bool):
            return verify_client_nid

        partner_update_data = self.get_update_data(
            customer,
            partner_tupande_id,
            gender,
            picture,
            country_id,
            company_id,
        )
        if client_id and not verify_client_id:
            return self.client_does_not_exist_response(customer)

        if (
            client_id
            and partner_phone_id
            and (partner_phone_id.id == partner_tupande_id.id)
        ):
            return self.update_client_details(
                partner_phone_id, partner_update_data, customer
            )

        if (partner_phone_id or partner_tupande_id) and not client_id:
            return self.client_already_exists_response(customer, partner_tupande_id)

        if not partner_phone_id and client_id and partner_tupande_id:
            return self.update_client_details(
                partner_tupande_id, partner_update_data, customer
            )

        if (
            partner_phone_id
            and client_id
            and partner_tupande_id
            and (partner_phone_id.id != partner_tupande_id.id)
        ):
            return self.client_phone_number_exists_response(
                customer, partner_tupande_id, phone_number_message
            )

        if not client_id:
            return self.create_partner(
                customer,
                gender,
                picture,
                country_id,
                company_id,
                res_partner,
                client_id,
            )

        return self.client_does_not_exist_response(customer)

    def get_partner_phone_id(self, customer, res_partner):
        if customer.get("phoneNumber"):
            return res_partner.search(
                [("phone", "=", customer.get("phoneNumber"))], limit=1
            )
        return False

    def get_partner_tupande_id(self, customer, res_partner):
        return res_partner.search(
            [("tupande_client_id", "=", customer.get("id"))], limit=1
        )

    def verify_client_id(self, client_id, res_partner):
        return res_partner.search([("id", "=", int(client_id))], limit=1)

    def verify_client_nid(self, customer, res_partner):
        if customer.get("nid"):
            pattern = r"^\d{7,8}$"
            if bool(re.match(pattern, customer.get("nid"))):
                existing_nid = res_partner.search(
                    [("nid", "=", int(customer.get("nid")))], limit=1
                )
                if existing_nid:
                    return {
                        "httpStatusCode": "400",
                        "id": customer.get("id"),
                        "odoo-id": existing_nid.id,
                        "message": f"Client with the NID: {existing_nid.nid} "
                        "provided already exist",
                    }
                return False
            else:
                return {
                    "httpStatusCode": "400",
                    "id": customer.get("id"),
                    "odoo-id": False,
                    "message": f"The NID: {customer.get('nid')} provided is not valid",
                }
        return False

    def get_phone_number_message(self, customer):
        return (
            "Client with phoneNumber "
            + str(customer.get("phoneNumber"))
            + "  already exists."
        )

    def client_already_exists_response(self, customer, partner_id):
        return {
            "httpStatusCode": "400",
            "id": customer.get("id"),
            "odoo-id": partner_id.id,
            "message": "Client with the details provided already exist",
        }

    def client_phone_number_exists_response(
        self, customer, partner_id, phone_number_message
    ):
        return {
            "httpStatusCode": "400",
            "id": customer.get("id"),
            "odoo-id": partner_id.id,
            "message": phone_number_message,
        }

    def client_does_not_exist_response(self, customer):
        return {
            "httpStatusCode": "400",
            "id": customer.get("id"),
            "odoo-id": False,
            "message": "Client with the details provided does not exist",
        }

    def create_partner(
        self, customer, gender, picture, country_id, company_id, res_partner, client_id
    ):
        try:
            partner_create_data = self.get_create_data(
                customer, gender, picture, country_id, company_id
            )
            partner_id = res_partner.create(partner_create_data)
        except Exception as e:
            return {
                "httpStatusCode": "400",
                "id": customer.get("id"),
                "odoo-id": False,
                "message": f"Client is not created due to an exception {str(e)}",
            }
        return {
            "httpStatusCode": "201",
            "id": customer.get("id"),
            "odoo-id": partner_id.id,
            "message": (
                "Your client was not exist on odoo before, Its created now"
                if client_id
                else "Client created successfully on odoo"
            ),
        }

    def update_client_details(self, partner_id, partner_update_data, customer):
        update_message = "Client Details updated successfully"
        try:
            partner_id.sudo().update(partner_update_data)
            return {
                "httpStatusCode": "200",
                "id": customer.get("id"),
                "odoo-id": partner_id.id,
                "message": update_message,
            }
        except Exception as e:
            return {
                "httpStatusCode": "400",
                "id": customer.get("id"),
                "odoo-id": False,
                "message": f"Client is not updated due to an exception {str(e)}",
            }
