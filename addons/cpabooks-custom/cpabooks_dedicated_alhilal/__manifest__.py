{
    'name': "CPABooks Dedicated Al-Hilal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Tanvir Islam",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'professional_templates_v1',
        'account',
        'dev_invoice_multi_payment',
        'mail',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/ir_sequence.xml',
        'wizard/create_payment_certificate_wizard_view.xml',
        'wizard/certificate_payment_view.xml',
        'views/payment_certificate_view.xml',
        'views/account_move_view_inherit.xml',
        'views/report_template_settings_view_inherit.xml',
        'reports/reports.xml',
        'reports/report_payment_certificate_template.xml',
        'reports/invoice_common_template_v1.xml',
        'reports/odoo_template_cp_inherit.xml',
        'reports/no_header_footer_cp_po_template_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
