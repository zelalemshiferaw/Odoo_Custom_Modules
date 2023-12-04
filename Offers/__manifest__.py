{
	'name': "Offers",
	'version': '1.0',
    'summary': """
       Odoo Pos Offers Module
       """,
    'description': """
       Odoo Pos Offers Module
    """,
	'author': "Zelalem Shiferaw",
	'depends': ['base','product','point_of_sale'],
	'data': [
		'security/ir.model.access.csv',	 
		'views/offer.xml',
		'views/assets.xml',
		'data/pos_offer_scheduler.xml'
	],
    'images': ['static/src/img/offer.jpg'],
    'qweb': ['static/src/xml/receipt.xml'],
	'installable': True,
	'application': True,
	'auto_install': False,
  
}
