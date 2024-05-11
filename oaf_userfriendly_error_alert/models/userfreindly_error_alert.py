from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

# Define a custom model to extend the pos.order model
class ExtendedPosOrder(models.Model):
    _inherit = 'pos.order'

    # Override the create method to handle exceptions
    @api.model
    def create(self, vals):
        try:
            return super(ExtendedPosOrder, self).create(vals)
        except Exception as e:
            # User-friendly message to display in case of an exception
            userfriendly_message = _("Oops! We couldn't save the sale at this time. Please try again."
                              " If the issue persists, please notify a manager or contact our support team for assistance. "
                              "Thank you for your understanding")

            raise UserError(userfriendly_message)

# Define a custom model to extend the res.partner model
class ExtendedResPartner(models.Model):
    _inherit = 'res.partner'

    # Override the create method to handle exceptions
    @api.model
    def create(self, vals):
        try:
            return super(ExtendedResPartner, self).create(vals)
        except Exception as e:
            # User-friendly message to display in case of an exception
            userfriendly_message = _("Apologies, we encountered an issue creating the customer profile on the POS system. "
                              "Please try again. If the problem persists, kindly contact our support team for assistance."
                              " Thank you for your patience")
            raise UserError(userfriendly_message)
