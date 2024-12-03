# -*- coding: utf-8 -*-
{
    "name": "Tupande Odoo Connector",
    "summary": """
        Syncing data between Tupande and odoo with rest API
        sale order and client""",
    "description": """
        Handling syncing form tupande to odoo.
        Sale order and Client
    """,
    "author": "Usman Akbar",
    "website": "https://oneacrefund.org/",
    # for the full list
    "category": "Customization",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "ce_portal", "rest_api"],
    # always loaded
    "data": [
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
}
