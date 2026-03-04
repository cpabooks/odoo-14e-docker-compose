# -*- coding: utf-8 -*-



{
    'name': "CPABooks Tally",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "CPABooks",
    'website': "https://www.cpabooks.org/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tally',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base','project_task_approve'],
    'depends': [
        'base',
        'account',
        'dynamic_xlsx',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/tally_kanban_view.xml',
        'views/display_menu.xml',
        'views/assets.xml',
        'views/revise_chart_of_account.xml',
        'views/vat_summary_year_view.xml',
        'views/vat_summary_report_view.xml',
        'views/statistics_kanban_view.xml',
        'wizard/alter_wizard_view.xml',
        'views_mis_budget/mis_budget_views.xml',
        'data/cpabooks_tally_demo_data.xml',
        'data/vat_summary_year_data.xml',
        # 'data/vat_summary_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    # 'image': 'cpabooks_tally/static/description/icon.png'
}
