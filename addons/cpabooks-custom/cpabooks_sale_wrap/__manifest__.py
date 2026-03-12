# -*- coding: utf-8 -*-
{
    'name': "CPABOOKS Sale Wrap",

    'summary': """
        This module will sove the text wrapping problem in sale module""",

    'description': """
        This module will sove the text wrapping problem in sale module
    """,

    'author': "CPABOOKS",
    'website': "https://www.cpabooks.org/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'views/sale_order_inherit.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
