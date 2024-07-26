{
    'name': "Pallet Portal",
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'author': "Zelalem Shiferaw",
    'depends': ['portal', 'stock', 'contacts',
                'website_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_pallet_templates.xml',
        'views/views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
