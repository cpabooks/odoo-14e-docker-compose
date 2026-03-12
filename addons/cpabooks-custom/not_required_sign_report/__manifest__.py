# -*- coding: utf-8 -*-
{
    'name': "Not Required Sign in Report",

    'summary': """
Sign and Serial No. Report""",

    'description': """
        invoice extra field invoice module's purpose
    """,

    'author': "Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
