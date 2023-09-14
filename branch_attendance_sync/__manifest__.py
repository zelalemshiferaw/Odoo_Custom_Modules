{
    'name': 'Branch Attendance Sync',
    'version': '1.1',
    'author': "zelalemshiferaw71921@gmail.com",
    'summary': 'Sync Attendance To Centeral',
    'description': """ 
            """,
    'depends': ['hr','hr_attendance'],
    'category': 'Extra',
    'sequence': 1,
    'data': [
        'views/menus.xml',
        'security/ir.model.access.csv'
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}
