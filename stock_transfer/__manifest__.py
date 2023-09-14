{
    'name': 'Stock Transfer Request',
    'version': '1.1',
    'summary': 'Stock transfer request',
    'description': """ 
                    This module allows users to generate transfer requests for moving
                    stock between locations. Key features include:

                    - Request approval workflow with multiple approval levels
                    - Ability to filter and search transfer requests
                    - Auto-generate picking on approval 
                    - Track transfer request status
                    - Integrated with stock
                    """,
    'depends': ['mail','stock','base','web_notify'],
    'category': 'Extra',
    'author' : 'Zelalemshiferaw71921@gmail.com',
    'sequence': 1,
    'data': [
        'security/ir.model.access.csv',
        'sequences/sequences.xml',
        'report/report_template.xml',
        'report/reports.xml',
        'data/ir.cron.data.xml',        
        'views/assets.xml',
        'views/menus.xml',

    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}



