# -*- coding: utf-8 -*-
{
    'name': "xx_cpabooks_signature",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "BAHARTUTUL",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'], #, 'professional_templates'

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/signature_setup.xml',
        'views/templates.xml',
        'views/sale_order.xml',
        'report/invoice_report_inherit.xml',
        'report/sale_report_inherit.xml',
        'report/purchase_report_inherit.xml',
        # 'report/sale_common_report_template_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
