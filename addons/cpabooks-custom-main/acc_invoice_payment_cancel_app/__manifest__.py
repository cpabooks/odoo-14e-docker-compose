# -*- coding: utf-8 -*-
{
    'name': 'Cancel Invoice Cancel Account Payment',
    "author": "Edge Technologies",
    'version': '14.0.1.2',
    'live_test_url': "https://youtu.be/uOSKKPrAzPY",
    "images":['static/description/main_screenshot.png'],
    "summary" : 'Invoice Cancel Payment Cancel Journal Entry Cancel Journal Entries Customer Invoice Cancel Vendor Bill Cancel Bill Payment Cancel Invoicing Cancel Accounting Payment Cancel All in One Account Cancel Delete Invoice Delete Payment',
    'description': """ 
        Cancel Invoice | Cancel Payment
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','hr_expense'],
    'data': [ 
        'security/security.xml',
        'views/account_move_action.xml',
        'views/account_payment_action.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',      
        'views/hr_expense.xml',
        'views/acccount_payment_register.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 12,
    'currency': "EUR",
    'category': 'Accounting',

}

