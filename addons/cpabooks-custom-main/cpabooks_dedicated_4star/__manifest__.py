{
    'name': "Cpabooks Dedicated 4Star",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Tanvir Islam",
    'website': "https://github.com/tanvirislamchayan",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'professional_templates_v1'],

    # always loaded
    'data': [
        'security/import_purchase_user.xml',
        'security/ir.model.access.csv',
        'views/import_purchase_view.xml',
        'views/purchase_order_view.xml',
        'views/account_move.xml',
        'views/menuitem.xml',
        'views/dot_matrix_template_configur_view.xml',
        'views/res_partner_extra_vew.xml',
        'views/res_partner_view.xml',
        'views/customer_code_setup_views.xml',
        'views/sale_order.xml',
        'wizard/bulk_res_partner_export_view.xml',
        'reports/odoo_template_cp.xml',
        'reports/invoice_line_template.xml',
        'views/assets.xml',
        'reports/invocie_dot_matrix_report_template.xml',
        'reports/reports.xml',
        'data/dot_matrix_template_data.xml',
        'data/data_customer_cudo_setup.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
