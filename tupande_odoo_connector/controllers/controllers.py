import json
import logging

from odoo import http
from odoo.addons.rest_api.controllers.main import (
    check_permissions,
    error_response,
    successful_response,
)
from odoo.http import request

_logger = logging.getLogger(__name__)


class TupandeResPartnerController(http.Controller):
    @http.route(
        ["/tupande/client", "/tupande/client/<int:client_id>"],
        methods=["POST"],
        type="http",
        auth="none",
        csrf=False,
    )
    @check_permissions
    def tupande_client_creation(self, client_id=False):
        cr = request.cr
        uid = request.session.uid
        try:
            odoo_response = json.loads(request.httprequest.data)
        except Exception as e:
            return error_response(
                400,
                "Payload is causing issue",
                {
                    "response": "Request Payload is causing issue",
                    "Exception Is": str(e),
                    "Payload Is": str(request.httprequest.data),
                },
            )

        company_id = (
            request.env(cr, uid).ref("oaf_countries_and_companies.company_loc_kenya").id
        )
        country_id = request.env(cr, uid).ref("base.ke").id
        res_partner = request.env(cr, uid)["res.partner"].sudo()
        _logger.info(odoo_response)
        bulk_update = not isinstance(odoo_response, dict)
        if not bulk_update:
            response = res_partner.handle_client_info(
                odoo_response, res_partner, country_id, company_id, client_id
            )
            if int(response.get("httpStatusCode")) not in [201, 200]:
                return error_response(
                    int(response.get("httpStatusCode")),
                    "Failed to create Client",
                    {
                        "odoo_response": response.get("message"),
                    },
                )

            return successful_response(
                status=int(response.get("httpStatusCode")), dict_data=response
            )
        elif client_id:
            return error_response(
                400,
                "You should send Json format if you want to update client",
                {
                    "response": "Request Payload is causing issue",
                    "Payload Is": str(request.httprequest.data),
                },
            )

        response = []
        for commit_data, customer in enumerate(odoo_response, start=1):
            if commit_data % 50 == 0:
                request.env.cr.commit()

            response.append(
                res_partner.handle_client_info(
                    customer, res_partner, country_id, company_id
                )
            )
        return successful_response(status=200, dict_data={"response": response})
