from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError
import logging
_logger=logging.getLogger(__name__)

class ProductInherit(models.Model):
    _inherit="product.template"

    is_offer = fields.Boolean(string='Is Offer',defualt=False)
    list_of_offer_products = fields.Char(string="Offer Items", compute='_compute_offer_items')

    # Get list of items for receipt display
    @api.depends('is_offer')
    def _compute_offer_items(self):
        for product in self:
            if product.is_offer:
                offer = self.env['pos.offer'].search([('name', '=', product.id)])
                product.list_of_offer_products = ', '.join([f'{item.name.name} ({item.quantity})' for item in offer.offer_items])
            else:
                product.list_of_offer_products = ''




class Offer(models.Model):
    _name = 'pos.offer'
    
    name = fields.Many2one('product.template', string='Offer Product')
    price = fields.Float(string='Price')
    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')
    offer_items = fields.One2many('offer.item', 'offer', string='Offer Items')
    offer_description = fields.Char("Offer Descritption")    

    @api.model
    def create(self, vals):
        name = vals.get('name')
        if name and self.search([('name', '=', name)]):
            raise UserError('offer product already exists.')
        offer = super(Offer, self).create(vals)
        # Update the is_offer field in the related product
        if offer.name:
            offer.name.is_offer = True
        return offer

    def write(self, vals):
        if 'name' in vals:
            name = vals.get('name')
            if name and self.search([('name', '=', name), ('id', '!=', self.id)]):
                raise UserError('Offer product already exists.')
        return super(Offer, self).write(vals)

    @api.onchange('price')
    def _onchange_price(self):
        if self.name:
            self.name.lst_price = self.price

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.name and self.date_from and self.date_to:
            today = datetime.datetime.now()
            if self.date_from <= today <= self.date_to:
                self.name.write({'available_in_pos': True})
            else:
                self.name.write({'available_in_pos': False})
        elif self.name:
            self.name.write({'available_in_pos': False})

    @api.model
    def update_available_in_pos(self):
        today = datetime.datetime.now()
        expired_offers = self.search([('date_to', '<', today), ('name.available_in_pos', '=', True)])
        expired_offers.name.write({'available_in_pos': False})



class OfferItem(models.Model):
    _name = 'offer.item'
    
    name = fields.Many2one('product.template', string='Product')
    sale_price = fields.Float(string='Sale Price')
    quantity = fields.Integer(string='Quantity')
    offer = fields.Many2one('pos.offer', string='Offer')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, vals):
        order = super(PosOrder, self).create(vals)
        order_lines_to_create = []
        order_lines_to_unlink = []

        for line in order.lines:
            check_is_offer=self.env['pos.offer'].search([('name', '=', line.product_id.id)])
            if check_is_offer:
                offer = self.env['pos.offer'].search([('name', '=', line.product_id.id)])

                for offer_item in offer.offer_items:
                    order_line_vals = {
                        'order_id': order.id,
                        'product_id': offer_item.name.id,
                        'full_product_name':offer_item.name.name,
                        'price_unit': offer_item.sale_price,
                        'qty': offer_item.quantity*line.qty,
                        'price_subtotal':offer_item.sale_price * offer_item.quantity,
                        'price_subtotal_incl':offer_item.sale_price * offer_item.quantity,
                        'tax_ids_after_fiscal_position':[(6, 0,offer_item.name.taxes_id.ids)]
                    }
                    order_lines_to_create.append((0, 0, order_line_vals))

        
                            
                for line in order.lines:
                    check_is_offer = self.env['pos.offer'].search([('name', '=', line.product_id.id)])
                    if check_is_offer:
                        order_lines_to_unlink.append((2, line.id))

                if order_lines_to_unlink:
                    order.write({'lines': order_lines_to_unlink})

        if order_lines_to_create:
            order.write({'lines': order_lines_to_create})        
        return order









