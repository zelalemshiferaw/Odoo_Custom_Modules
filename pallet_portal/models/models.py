from odoo import models, fields, api, _
from datetime import datetime

class StockQuantPallet(models.Model):
    """Inherit the model to add field"""
    _inherit = 'stock.quant.package'

    url = fields.Char("URL", compute="_compute_url", store=True)
    
    @api.depends('name')
    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.url = f"{base_url}/web#id={record.id}&model={self._name}&view_type=form"

""" 
    Stock Location inherited to resolve permission issues
    when public customers attempt to view their pallets
"""
class StockLocation(models.Model):
    _inherit = 'stock.location'
