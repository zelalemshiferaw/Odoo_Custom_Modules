# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
import re

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    on_product_line = fields.Boolean("Add notes to individual orderlines", default=True)
    on_order = fields.Boolean("Add note to the complete order", default=True)
    on_order_mandatory = fields.Boolean("Complete order note mandatory")
    wk_mpesa_regex = fields.Char(
        "Mpesa Regex",
        default="^[A-Za-z]{0,3}[0-9]{1,3}[A-Za-z]{1,2}[0-9]{0,3}[A-Za-z]{1,5}[0-9]{0,3}[A-Za-z]{0,3}$",
    )
    wk_mpesa_length = fields.Integer("Mpesa Code Length", default="10")
    receipt_order_note = fields.Boolean("Print notes on the receipt", default=True)
    note_keyword_limit = fields.Integer(string="Note Keywords Limit")
    set_note_keyword_limit = fields.Boolean()


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return.update({"note": ui_order.get("order_note", "")})
        return fields_return

    @api.model
    def wk_check_mpesa_code(self, kwargs):
        mpesa_code = kwargs.get("mpesa_code")
        # ---------------------Checked if Code is valid-----------------------
        regex = f'{kwargs.get("wk_mpesa_regex")}'
        code_length = kwargs.get("wk_mpesa_length")
        if not re.match(regex, mpesa_code) or len(mpesa_code) != code_length:
            return {
                "error": True,
                "message": "Please enter a valid mpesa code.",
            }
        # ---------------------Checked if Code is unique or not-----------------------
        pos_order = self.search([("note", "=", mpesa_code)])
        return (
            {
                "error": True,
                "message": "Please enter a unique mpesa code. This code has already been used.",
            }
            if pos_order
            else {"error": False}
        )


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    order_line_note = fields.Text("Extra Comments")

    @api.model
    def _order_line_fields(self, line, session_id=None):
        fields_return = super(PosOrderLine, self)._order_line_fields(
            line, session_id=None
        )
        fields_return[2].update({"order_line_note": line[2].get("order_line_note", "")})
        return fields_return
