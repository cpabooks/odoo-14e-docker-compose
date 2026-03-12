# -*- coding: utf-8 -*-
{
    'name': "Freight Inquery",

    'summary': """
freight inquery for quotation and job""",

    'description': """
        For Quotation and invoice extra field for Freight module's purpose
    """,

    'author': "Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'sale_management','freight'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/freight_inquery.xml',
        # 'report/inquery_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
