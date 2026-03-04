# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Sale Discount With Tax PT V1",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_management','account','stock','professional_templates_v1'],
    'data': [
        'views/sale_view.xml',
        'report/invoice_common_professional_template.xml',
        'report/common_quotation_template.xml',
        # 'report/inherit_sale_report.xml',
        # 'report/inherit_account_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
