# -*- coding: utf-8 -*-
{
    'name': "Cpabooks User Permission (Menu, buton, etc permssion)",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Kamrul Hasan",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale_management', 'purchase', 'cpabooks_switchgear_custom', 'bi_material_purchase_requisitions'],

    # always loaded
    'data': [
        'security/groups.xml',
        'views/menu_group.xml',
    ]
}
