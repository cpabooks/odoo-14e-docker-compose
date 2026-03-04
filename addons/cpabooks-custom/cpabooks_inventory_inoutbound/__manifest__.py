# -*- coding: utf-8 -*-
{
    'name': "CPAbooks Inventory Inbound & Outbound ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Kamrul Hasan",
    'website': "http://www.cpabooks.org",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'product_expiry','eq_inventory_valuation_report',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/report_paperformat.xml',
        'views/stock_production_lot.xml',
        #'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/stock_move.xml',
        'views/inventory_reporting.xml',
        'views/stock_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
