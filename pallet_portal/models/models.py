from odoo import models, fields, api, _
from datetime import datetime

class StockQuantPallet(models.Model):
    _inherit = 'stock.quant.package'
    _name = 'stock.quant.pallet'

    name = fields.Char(
        'Pallet Reference', copy=False, index='trigram', required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.quant.pallet') or _('Unknown')
    )

    location_id = fields.Many2one('stock.location', 'Location', index=True, readonly=False, store=True)
    partner_id = fields.Many2one('res.partner', string="Partner", ondelete='cascade')
    picking_id = fields.Many2one('stock.picking', string="Picking", ondelete='cascade')
    barcode = fields.Char(string='Barcode', help="Barcode for Scanning Product")
    image = fields.Binary(
    string="Image",
    store=True,
    attachment=False
    )
    content = fields.Char(string="Content of the pallet")
    display_name = fields.Char(string="Name", compute="_compute_name")
    stored_days = fields.Integer(string="Days in storage", compute="_compute_stored_days")
    move_line_id = fields.Many2one('stock.move.line', string="Move Line",ondelete='cascade')
    released_date = fields.Datetime(string='Released Date', help="Date package was released to client")

    state = fields.Selection([
        ('storage', 'In storage'),
        ('pending', 'Pending delivery'),
        ('released', 'Released to client'),
        ('damaged', 'Damaged in storage')
    ], string='State', default='storage', index=True)

    @api.depends('name')
    def _compute_name(self):
        for record in self:
            record.display_name = record.name or _('Unknown')

    @api.depends('released_date')
    def _compute_stored_days(self):
        for record in self:
            if record.released_date:
                released_date = fields.Datetime.from_string(record.released_date)
                today = datetime.now()
                stored_days = (today - released_date).days
                record.stored_days = stored_days
            else:
                record.stored_days = 0




""" 
    Stock Location inherited to resolve permission issues
    when public customers attempt to view their pallets
"""
class StockLocation(models.Model):
    _inherit = 'stock.location'
