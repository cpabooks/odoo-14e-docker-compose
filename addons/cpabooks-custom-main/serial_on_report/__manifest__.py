# -*- coding: utf-8 -*-
{
    'name': "xx_Cpabooks Serial in Report",

    'summary': """
Serial only in Report""",

    'description': """
        extra data freight module's purpose
    """,

    'author': "Md. Shaheen Hossain",
    'website': "http://www.eagle-erp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/invoice_sl_no_view.xml',
        'views/quotation_sl_no_view.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
