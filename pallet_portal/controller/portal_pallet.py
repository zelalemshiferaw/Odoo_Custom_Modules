from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from collections import OrderedDict


class CustomerPortal(portal.CustomerPortal):
    """This class inherits controller portal"""
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'pallet_count' in counters:
            # Update the count of StockQuantPallet records
            pallet_count = request.env['stock.quant.pallet'].search_count([('partner_id.id', '=', request.env.user.partner_id.id)])
            values['pallet_count'] = pallet_count
        
        return values

    @http.route(['/my_pallet', '/my_pallet/page/<int:page>'], type='http', auth="user", website=True)
    def my_pallet_portal(self, filterby=None, sortby='date',groupby="none"):
        """To add filter and sorting for records in the website portal"""
        

        searchbar_sortings = {
            'date': {'label': _('Created date'), 'order': 'create_date desc'},
            'stored_days': {'label': _('Storage Date'), 'order': 'stored_days'},
            'released_date': {'label': _('Released Date'), 'order': 'released_date'},
        }

        if sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': 'All', 'domain': []},
            'storage': {'label': 'In storage', 'domain': [('state', '=', 'storage')]},
            'pending': {'label': 'Pending delivery', 'domain': [('state', '=', 'pending')]},
            'released': {'label': 'Released to client', 'domain': [('state', '=', 'released')]},
            'damaged': {'label': 'Damaged in storage', 'domain': [('state', '=', 'damaged')]},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # Combine domain and sort order in the search query
        my_pallets = request.env['stock.quant.pallet'].sudo().search(
            [('partner_id.id', '=', request.env.user.partner_id.id)] + domain,   # Combining partner and domain filters
            order=order
        )

        total_pallets = len(my_pallets)

        page_detail = pager(
            url='/my_pallet', total=total_pallets, 
            url_args={'filterby': filterby, 'sortby': sortby,'groupby':groupby}
        )

        return request.render("pallet_portal.portal_pallet", {
            'pallets': my_pallets,
            'page_name': 'my_pallet',
            'pager': page_detail,
            'default_url': '/my_pallet',
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
