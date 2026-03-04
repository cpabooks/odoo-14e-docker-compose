# -*- coding: utf-8 -*-
{
    'name': "Freight Field in Quotation",

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
    'depends': ['base', 'account', 'sale', 'sale_management','freight', 'account', 'many2many_tags_link'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/freight.container.type.csv',
        'data/freight.charge.type.csv',
        'data/freight.charge.csv',
        'data/freight.port.csv',
        # 'views/templates.xml',
        # 'report/vehicle_report.xml',
        'report/quotation_report.xml',
        'report/invoice_report.xml',
        'report/freight_invoice_report.xml',
        'data/freight_product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
