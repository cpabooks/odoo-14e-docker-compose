# -*- coding: utf-8 -*-
{
    'name': "CPABooks Tailoring Custom",

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
    'depends': ['base', 'crm', 'stock', 'mail', 'sale', 'project'],

    # always loaded
    'data': [

        'views/sale_order.xml',
        'views/views.xml',
        'views/templates.xml',
        'data/flowchart_kanban_data.xml',
        'views/flowchart_views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/sale_order.xml',
        'demo/demo.xml',
    ],
}
