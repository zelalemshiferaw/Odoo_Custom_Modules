# -*- coding: utf-8 -*-

import re
from datetime import datetime

import pytz
from odoo import fields, models
from odoo.addons.rest_api.controllers.main import error_response, successful_response


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tupande_sale_ref = fields.Char(string="Tupande ID")

    def get_partner_tupande(self, order_payload, partner, company_id, country_id):
        """
        This function is used to create client if not exist
        Plus if phone number is match but tupande id is not found,
         it applies tupande_client_id

        returns: partner_id
        """

        phone_number = partner.phone_format(
            order_payload["phoneNumber"], self.env.ref("base.ke")
        )
        partner_id = partner.sudo().search(
            [("tupande_client_id", "=", order_payload.get("clientId"))],
            limit=1,
        )

        partner_phone_id = partner.sudo().search(
            [("phone", "=", order_payload.get("phoneNumber"))], limit=1
        )
        if not partner_id and partner_phone_id:
            partner_phone_id.update(
                {
                    "tupande_client_id": int(order_payload.get("clientId")),
                }
            )
            partner_id = partner_phone_id

        elif not partner_id and not partner_phone_id:
            try:
                if not re.match(r"(0|\+?254)7\d{8}", order_payload.get("phoneNumber")):
                    return {
                        "httpStatusCode": "400",
                        "id": order_payload.get("id"),
                        "odoo-id": False,
                        "parameterName": "phone",
                        "message": "Client was not exist, while creating"
                        " the client You phone number "
                        "didn't match with right pattern",
                    }
                partner_id = partner.create(
                    {
                        "tupande_client_id": int(order_payload.get("clientId")),
                        "firstname": order_payload.get("firstName"),
                        "lastname": order_payload.get("lastName"),
                        "activation_date": str(datetime.now().date()),
                        "nid": order_payload.get("nid"),
                        "contact_type": "contact",
                        "state": "inactive",
                        "credit_client": True,
                        "country_id": country_id,
                        "company_id": company_id,
                        "phone": phone_number,
                    }
                )
            except Exception as e:
                return {
                    "httpStatusCode": "400",
                    "id": order_payload.get("id"),
                    "odoo-id": False,
                    "parameterName": "phone",
                    "message": f"Client was not exist, while creating"
                    f" the client we got this exception{e}",
                }
        return partner_id

    def any_parameter_missing(self, required_parameters, kwargs):
        if not all(
            parameter in list(kwargs.keys()) for parameter in required_parameters
        ):
            return error_response(
                400,
                "Pass the required parameters"
                "(clientId, firstName, lastName, nid, orderRef,"
                " phoneNumber, orderLines)",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "10007": "Pass the required parameters"
                        "(clientId, firstName, lastName, nid, orderRef,"
                        " phoneNumber, orderLines, shopId, channelId)"
                    },
                },
            )

        if kwargs.get("channelId") and kwargs.get("shopId"):
            try:
                int(kwargs.get("channelId"))
                int(kwargs.get("shopId"))
            except Exception as e:
                return error_response(
                    400,
                    "Make sure that shopId and clientId should be Integer",
                    {
                        "tupande_order_ref": kwargs.get("orderRef"),
                        "odoo_id": False,
                        "error_code": {
                            "100016": f"Make sure that shopId and "
                            f"clientId should be Integer Exception {str(e)}"
                        },
                    },
                )

        channel_id = self.env["oaf.channels"].search(
            [("id", "=", int(kwargs.get("channelId")))], limit=1
        )
        if not channel_id:
            return error_response(
                400,
                "Channel not found in odoo",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "100016": "Channel id "
                        + str(kwargs.get("channelId"))
                        + " not exit in odoo"
                    },
                },
            )

        shop_id = self.env["res.shop"].search(
            [("id", "=", int(kwargs.get("shopId")))], limit=1
        )
        if not shop_id:
            return error_response(
                400,
                "Shop not found in odoo",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "100017": "Shop id "
                        + str(kwargs.get("shopId"))
                        + " not exit in odoo"
                    },
                },
            )
        else:
            return False

    def handle_order_tupande(
        self,
        order_vals,
        order_lines_data,
        company_id,
        kwargs,
        product_id,
        order_line_id,
    ):
        """
        This function create sale order and there line.
        In case some issue happen while creating order or order line response 400.
        for successful creation it has 3 scenarios.
        1- If any product not found on odoo it response to tupande.
        2- Check reserved Qty and based upon that send status.
        3- Everything goes right
        returns: error_response(
            400, "Order Line is not created on odoo due to some exceptional",
            {'tupande_order_ref': kwargs.get('orderRef'),
              "odoo_id": False,
              'error_code': '10012',
              'response': "Order Line is not created on odoo due to some exceptional"
              })
        """
        print()
        try:
            order_id = (
                self.with_context(is_migrated=True)
                .with_company(company_id)
                .sudo()
                .create(order_vals)
            )

        except Exception as e:
            return error_response(
                400,
                "Order is not created on odoo due to some exceptional",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "100011": f"Order is not created on "
                        f"odoo due to some exceptional{str(e)}"
                    },
                },
            )
        order_lines_dict = {}
        response_qty = self.tupdande_order_line(
            order_id,
            product_id,
            order_lines_data,
            order_line_id,
            order_lines_dict,
        )

        if isinstance(response_qty, dict):
            return error_response(
                400,
                "Order Line is not created on odoo due to some exceptional",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "10012": "Order Line is not created on odoo"
                        " due to some exceptional" + response_qty.get("error")
                    },
                },
            )
        tupande_order_response = {
            "status": {"id": 2, "value": "Confirmed"},
            "orderRef": kwargs.get("orderRef"),
            "createdDate": str(order_id.create_date.replace(tzinfo=pytz.utc)),
            "clientId": kwargs.get("clientId"),
            "clientPhoneNumber": kwargs.get("phoneNumber"),
            "orderId": order_id.name,
            "shopId": kwargs.get("shopId"),
            "channelId": kwargs.get("channelId"),
            "amountTotal": kwargs.get("amountTotal"),
            "totalQuantity": response_qty,
            "totalAwaitingFulfilment": 0,
            "totalFufilledQuantity": 0,
            "orderLines": list(order_lines_dict.values()),
        }
        order_id.with_context(is_migrated=True).action_confirm()
        total_reserved = 0
        if order_id.picking_ids:
            for line in order_id.picking_ids.move_ids_without_package:
                if order_lines_dict.get(line.product_id.default_code):
                    order_lines_dict[line.product_id.default_code]["status"] = {
                        "id": 300,
                        "value": "awaitingFulfillment",
                    }
                    if line.reserved_availability >= line.product_qty:
                        order_lines_dict[line.product_id.default_code]["status"] = {
                            "id": 320,
                            "value": "reservedAtShop",
                        }
                    order_lines_dict[line.product_id.default_code][
                        "reservedAtShop"
                    ] = line.reserved_availability
                total_reserved += line.reserved_availability
        tupande_order_response["totalReserevedAtShop"] = total_reserved

        return successful_response(201, tupande_order_response)

    def tupdande_order_line(
        self,
        order_id,
        product_id,
        order_lines_data,
        order_line_id,
        order_lines_dict,
    ):
        total_quantity = 0
        for line in order_lines_data:
            error_line = []
            product_id = product_id.sudo().search([("default_code", "=", line[0])])
            if product_id:
                try:
                    order_line_id.sudo().create(
                        {
                            "product_id": product_id.id,
                            "product_uom_qty": line[1],
                            "price_unit": line[2],
                            "order_id": order_id.id,
                        }
                    )
                except Exception as e:
                    order_id.sudo().action_cancel()
                    order_id.sudo().unlink()
                    return {"error": str(e)}
            else:
                error_line.append(
                    {"errorCode": 10920, "errorMessage": "Product not available"}
                )
            total_quantity += line[1]
            order_lines_dict[line[0]] = {
                "productCode": line[0],
                "productName": product_id.name,
                "totalQuantity": line[1],
                "unitPrice": int(line[2]),
                "reservedAtShop": 0,
                "fulfilledQauntity": 0,
                "lineErrors": error_line,
            }
        return total_quantity
