# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Product Image",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "S.M. BAHAR",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','cpabooks_custom_print','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/stock_picking.xml',
        # 'views/sale_order_optional_products.xml',
        'reports/sale_quotation_report.xml',
        'reports/invoice_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
