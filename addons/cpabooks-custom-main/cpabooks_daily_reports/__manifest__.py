# -*- coding: utf-8 -*-
{
    'name': "CPAbooks Daily Reports",

    'summary': """
        The "CPABooks Daily Reports" module for Odoo is designed to streamline 
        the process of generating detailed daily reports for various business 
        activities. With this module, users can easily create and customize 
        reports for sales, invoices, and purchases within a specified date range 
        by selecting a start date and an end date.
    """,

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
    'depends': ['base', 'account', 'web', 'account_asset'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/daily_invoice_report.xml',
        'views/daily_transaction_report_view.xml',
        'views/daily_sales_analysis_view.xml',
        'views/sequences.xml',
        'views/rent_contract_view.xml',
        'views/account_move_veiw_inherit.xml',
        'reports/reports.xml',
        'reports/daily_invoice_report_template.xml',
        'reports/daily_transaction_report_template.xml',
        'reports/A4_cpabooks_header_footer.xml',
        'reports/daily_sales_analysis_report_template.xml',
        'reports/rent_contract_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
