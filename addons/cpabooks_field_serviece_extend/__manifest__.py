# -*- coding: utf-8 -*-
{
    'name': "cpabooks_field_serviece_extend",

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
    'depends': [
        'base',
        'cpabooks_project_extend',
        'industry_fsm',
        'industry_fsm_report',
        'industry_fsm_sale',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/fsm_project_task.xml',
        'reports/worksheet_customer_report_templates.xml',
        'views/project_task_views.xml',
        'views/report_project_task.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
