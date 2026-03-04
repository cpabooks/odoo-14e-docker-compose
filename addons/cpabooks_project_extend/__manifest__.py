# -*- coding: utf-8 -*-
{
    'name': "Cpabooks Project Extend",

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
    'depends': ['project', 'base','sale','account','sale_project','hr_timesheet','planning','project_forecast', 'crm'],#,'sale_timesheet'
# cpabooks_switchgear_custom #'cpabooks_delivery_slip',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/create_default_stages.xml',
        'data/create_default_freq.xml',
        'data/task_seq.xml',
        'data/sequences.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/planning.xml',
        'views/project.xml',
        'views/project_task.xml',
        'views/res_config_settings.xml',
        'views/account_analytic_line.xml',
        # 'views/my_task_menuitems.xml',
        # 'reports/common_quotation_template.xml',
        'reports/delivery_report.xml',
        'reports/daily_task_report_template.xml',
        'reports/reports.xml',
        # 'views/account_account.xml',
        'wizard/task_update_wizard_view.xml',
        'wizard/task_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
