# -*- coding: utf-8 -*-
{
    'name': "Freight Field in Purchase",

    'summary': """
For Purchase extra field for Freight""",

    'description': """
        For For Purchase extra field for Freight module's purpose
    """,

    'author': "Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'sale_management','freight', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/freight_in_purchase.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
