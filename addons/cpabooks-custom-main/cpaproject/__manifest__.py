# -*- coding: utf-8 -*-
{
    'name': "Cpa Project in Project",

    'summary': """
for task extra column""",

    'description': """
        for task extra column for project module's purpose
    """,

    'author': "My Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
