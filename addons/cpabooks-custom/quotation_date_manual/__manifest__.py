# -*- coding: utf-8 -*-
{
    'name': "Modcom Manually Quotation date",

    'summary': """
For Quotation and invoice extra field for Freight""",

    'description': """
        For Quotation and invoice extra field for Freight module's purpose
    """,

    'author': "Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
