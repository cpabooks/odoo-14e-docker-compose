# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Job Order",

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
    'depends': ['base','sale','mail','cpabooks_sequences','mrp','cpabooks_switchgear_custom','cpabooks_custom_print','professional_templates'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/quotation.xml',
        'views/job_order.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        # 'views/mrp_bom.xml',
        'reports/report_menu.xml',
        # 'reports/sale_order_report.xml',
        # 'reports/mrp_bom_structure_report_without_value.xml',
        'reports/quotation_job_order_report.xml',
        'reports/common_invoice_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
