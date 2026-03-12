# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Dedicated Acme",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bahar",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','cpabooks_custom_print','cpabooks_delivery_slip','stock','bi_sale_discount_with_tax'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_picking.xml',
        # 'views/sale_order.xml',
        'report/sale_report_template.xml',
        'report/delivery_slip_report.xml',
        'report/invoice_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
