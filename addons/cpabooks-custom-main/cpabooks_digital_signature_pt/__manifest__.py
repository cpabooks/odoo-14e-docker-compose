# -*- coding: utf-8 -*-
{
    'name': "xx_Cpabooks Digital Signature PT",

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
    'depends': ['base','sale_management','purchase','account','stock','sign','professional_templates'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_digital_signature.xml',
        'views/purchase_digital_signature.xml',
        'views/inventory_digital_signature.xml',
        'views/invoice_digital_signature.xml',
        'views/res_users.xml',
        'views/signature_setup.xml',
        'reports/invoice_100_miles_template.xml',
        'reports/sale_100_miles_template.xml',
        'reports/common_invoice_template.xml',
        'reports/common_quotation_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
