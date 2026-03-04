# -*- coding: utf-8 -*-
{
    'name': "cpabooks_chart_of_accounts",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com\n\n
        
        This module includes updates to the following modules: \n
            `cpabooks_accounting_automation`,`cpabooks_sequences`,
            `cpabooks_tally`,`chart_of_accounts_v1`,`account_dynamic_reports`,`dynamic_xlsx`...

        If any of the listed modules are not installed, this module will automatically install them.
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
    'depends': ['base','account', 'cpabooks_accounting_automation', 'sh_pdc', 'account_asset', 'cpabooks_sequences'],

    # always loaded
    'data':[
        'views/inherit_account_account.xml',
        # 'views/delete_independent_coa.xml',
        # 'data/account.group.csv',
        # 'data/account.account.csv',
        # 'data/account.not.delete.csv',
        'views/views.xml',
        'views/coa_create.xml',
        'views/templates.xml',
        'views/chart_of_account_list.xml',
        'views/account_account.xml',
        'views/productTemplate.xml',
        'data/load_group.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
