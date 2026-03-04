# -*- coding: utf-8 -*-
{
    'name': "CPABooks Payment Certificate",

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
    'version': '14.0.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','product','project'],
# ,'cpabooks_job_order_extend'

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'data/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/payment_certificate.xml',
        'report/payment_certificate_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
