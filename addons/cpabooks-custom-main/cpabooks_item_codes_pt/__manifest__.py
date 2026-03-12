# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Item Codes PT",

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
    'depends': ['base','product','account','sale','stock','professional_templates'],

    # always loaded
    'data': [
        'views/item_code_product_view.xml',
        'views/item_code_product_product_view.xml',
        # 'views/invoice_sl_no_view.xml',
        # 'views/quotation_sl_no_view.xml',
        'views/item_code__on_invoice_report_inherit.xml',
        'views/item_code_on_quotation_report_inherit.xml',
        'views/inventory_report.xml',
        'views/report_settings.xml',
        'views/sale_order_line.xml',
        # 'reports/report_invoice_template.xml',
        # 'reports/report_contracting_invoice_report.xml',
        # 'reports/purchase_order_template.xml',
        'reports/common_invoice_line_template.xml',
        'reports/common_quotation_line_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
