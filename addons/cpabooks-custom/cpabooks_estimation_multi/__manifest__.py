# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Estimation Multi",

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
    'category': 'mrp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','cpabooks_switchgear_custom','cost_estimate_customer_ld','cpabooks_sequences'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/job_estimation.xml',
        'views/mrp_bom_line.xml',
        'views/mrp_production.xml',
        'reports/mrp_bom_report.xml',
        'reports/mrp_production_template.xml',
        'reports/job_estimate_report_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
