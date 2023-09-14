{
	'name': "Transfer and MRP Mass Validation",

	'summary': """
		Transfer and MRP Mass Validation""",

	'description': """
		This module is a game-changer for your manufacturing and inventory processes! With our Transfer and MRP Mass Validation, you can validate multiple MRP orders and transfers at once, saving you time and effort. Our unique feature allows you to validate based on the scheduled date in ascending order, ensuring that your production runs smoothly and efficiently. 

		Don't waste any more time manually validating each order or transfer	""",

	'author': "Etta/Zelalem",
    'data': [
        'views/mass.xml',
		'views/purchase_mass.xml',
        'security/ir.model.access.csv'
    ],
	'website': "https://odooethiopia.com",
	'category': 'Customizations',
	'version': '0.1',

	'depends': ['base','stock','mrp'],

}

