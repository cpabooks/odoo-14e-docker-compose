# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Dedicated Garden Perfume",

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
    'depends': ['base','account','stock','professional_templates','cpabooks_bank_details_pt','cpabooks_digital_signature_pt','cpabooks_project_extend', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/security.xml',
        'views/views.xml',
        'views/product_class.xml',
        'views/mrp_production_views.xml',
        'views/templates.xml',
        # 'views/invoice.xml',
        'views/product_template.xml',
        'data/data.xml',
        'views/sale_order.xml',
        'reports/common_quotation_line_template.xml',
        'reports/common_invoice_line_template.xml',
        'reports/common_quotation_template.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
