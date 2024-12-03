import ast
import json
import logging
from datetime import datetime

from odoo import http
from odoo.addons.rest_api.controllers.main import (
    check_permissions,
    error_response,
    rest_cors_value,
)
from odoo.http import request

_logger = logging.getLogger(__name__)


class TupandeSaleOrderController(http.Controller):
    @http.route(
        "/tupande/order",
        methods=["POST"],
        type="http",
        auth="none",
        csrf=False,
        cors=rest_cors_value,
    )
    @check_permissions
    def tupande_order_creation(self):
        """
        This function is the end point of tupande order creation API

        The function has 9 error codes
        10006: Client data is Missing
        10007: Some required parameters are missing
        10008: Client is not able to create on odoo
        10011: Order is not created on odoo due to some exceptional
        10012: Order Line is not created on odoo due to some exceptional
        10013: Order Line is not Fetch on odoo due to some exceptional
        10015: Order successfully created in odoo (order created successfully)
        10016: Product with ref number HR0po4599 not found on odoo (order created)
        10017: Product with ref number HR0po4599 prices change in odoo (order created)
        returns:{
        "tupande_order_ref": "S147561",
        "odoo_id": 50,
        "error_code": "10015",
        "response": "Order successfully created in odoo"
        }
        """
        cr, uid = request.cr, request.session.uid
        try:
            kwargs = json.loads(request.httprequest.data)
        except Exception as e:
            return error_response(
                400,
                "Payload cause issue",
                {
                    "response": "Request Payload is cause issue",
                    "Exception Is": str(e),
                    "Payload Is": str(request.httprequest.data),
                },
            )

        country_id = request.env.ref("base.ke").id
        company_id = request.env.ref("oaf_countries_and_companies.company_loc_kenya").id
        required_parameters = (
            "clientId",
            "firstName",
            "lastName",
            "orderRef",
            "phoneNumber",
            "orderLines",
            "shopId",
            "channelId",
            "orderDate",
        )
        sale_order = request.env(cr, uid)["sale.order"]
        missing_parameters = sale_order.any_parameter_missing(
            required_parameters, kwargs
        )

        if not isinstance(missing_parameters, bool):
            return missing_parameters

        partner = request.env(cr, uid)["res.partner"]
        partner_id = sale_order.get_partner_tupande(
            kwargs, partner, company_id, country_id
        )
        client_creation_error_message = "Client is not able to create on odoo"
        if not partner_id:
            return error_response(
                400,
                "Client is not able to create on odoo",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {"10008": client_creation_error_message},
                },
            )
        elif isinstance(partner_id, dict):
            return error_response(400, client_creation_error_message, partner_id)

        order_vals = {"partner_id": partner_id.id, "company_id": company_id}
        if kwargs.get("channelId"):
            order_vals["so_channel_id"] = int(kwargs.get("channelId"))

        if kwargs.get("loanProductId"):
            order_vals["loan_product_id"] = kwargs.get("loanProductId")

        order_vals["shop_id"] = int(kwargs.get("shopId"))
        order_vals["tupande_sale_ref"] = kwargs.get("orderRef")
        order_vals["date_order"] = str(
            datetime.strptime(kwargs.get("orderDate"), "%Y-%m-%dT%H:%MZ")
        )

        try:
            order_lines_data = ast.literal_eval(kwargs.get("orderLines"))
        except Exception as e:
            return error_response(
                400,
                "Order Line is not Fetch on odoo due to some exceptional",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": False,
                    "error_code": {
                        "10013": (
                            f"Order Line is not Fetch"
                            f" on odoo due to some exceptional{str(e)}"
                        )
                    },
                },
            )
        order_response = sale_order.search(
            [("tupande_sale_ref", "=", kwargs.get("orderRef"))]
        )
        product_id = request.env(cr, uid)["product.product"]
        order_line_id = request.env(cr, uid)["sale.order.line"]
        if not order_response:
            order_response = sale_order.handle_order_tupande(
                order_vals,
                order_lines_data,
                company_id,
                kwargs,
                product_id,
                order_line_id,
            )
        else:
            order_response = error_response(
                400,
                "Order Is already exist on odoo",
                {
                    "tupande_order_ref": kwargs.get("orderRef"),
                    "odoo_id": order_response.name,
                    "error_code": {"10013": "order is already exist in odoo"},
                },
            )
        return order_response
