{
    'name': "Pallet Portal",
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'author': "Zelalem Shiferaw",
    'website': 'https://www.example.com',
    'description': """
        This module provides a customer portal for managing pallet storage and delivery.

        Key Features:
        - View a list of all pallets stored in the warehouse
        - Filter pallets by status (in storage, released, pending, damaged)
        - Sort pallets by various criteria (creation date, storage date, release date)
        - View detailed pallet information, including location, images, and release dates
        - Secure user authentication to access the pallet management functionality
    """,
    'depends': [
        'portal',
        'stock',
        'contacts',
        'website_sale',
        'product',
        'iem_stock_picking_package'
    ],
    'data': [
        'views/portal_pallet_templates.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}