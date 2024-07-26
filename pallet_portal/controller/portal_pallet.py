from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    """This class inherits controller portal"""
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'p_count' in counters:
            # Update the count of StockQuantPallet records
            pallet_count = request.env['stock.quant.pallet'].search_count([('partner_id.id', '=', request.env.user.partner_id.id)])
            values['p_count'] = pallet_count
        
        return values

    @http.route('/my/pallet', type='http', auth="user", website=True)
    def portal_pallets(self, **kw):
        """Adding stock check option in portal"""
        pallets = request.env['stock.quant.pallet'].search([('partner_id.id', '=', request.env.user.partner_id.id)])  # Retrieve all StockQuantPallet records
        return request.render("pallet_portal.portal_pallet", {
            'pallets': pallets,
        })
