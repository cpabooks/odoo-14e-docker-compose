# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Custom Print v1 ykt",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "S. M. Emrul Bahar",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','professional_templates','account','hr'],

    # always loaded
    'data': [

        'views/views.xml',
        'views/templates.xml',
        'views/sale_order.xml',
        'views/hide_app.xml',
        'views/module_permission.xml',
        'views/account_move.xml',
        # 'views/project.xml',
        # 'views/res_users.xml',
        'report/sale_report_template.xml',
        'report/invoice_report_template.xml',
        'report/purchase_order_odoo_template.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
