# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Dedicated KCS",

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
    'depends': ['base','account','web','serial_on_report','sale','cpabooks_bank_details', 'sign'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/bank_details.xml',
        'views/res_company.xml',
        'views/account_payment.xml',
        'views/ir_attachment.xml',
        'reports/invoice_template.xml',
        'reports/sale_proforma_report.xml',
        'reports/report_payment_receipt_templates.xml',
        'reports/report_payment_receipt.xml',
        'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
