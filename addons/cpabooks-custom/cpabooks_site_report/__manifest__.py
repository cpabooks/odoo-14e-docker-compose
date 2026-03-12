# -*- coding: utf-8 -*-
{
    'name': "CPABooks Site Report",

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
    'version': '14.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'data/sequences.xml',
        'views/daily_site_report.xml',
        'views/weekly_site_report.xml',
        'views/monthly_site_report.xml',
        'views/supervisor_daily_report.xml',
        'views/supervisor_weekly_report.xml',
        'views/supervisor_monthly_report.xml',
        'views/client_report.xml',
        'views/templates.xml',
        'views/menuitem.xml',
        'report/daily_site_report_report.xml',
        'report/weekly_site_report_report.xml',
        'report/monthly_site_report_report.xml',
        'report/supervisor_daily_report_report.xml',
        'report/supervisor_weekly_report_report.xml',
        'report/supervisor_monthly_report_report.xml',
        'report/client_report_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
