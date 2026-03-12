# -*- coding: utf-8 -*-
{
    'name': 'Annual Maintenance Contract - AMC',
    'version': '14.0.0.1',
    'summary': """
        Annual Maintenance Contract - AMC""",

    'description': """
        Annual Maintenance Contract - AMC
    """,
    'category': 'Maintenance',
    'author': "Ethics Infotech LLP",
    'website': "http://www.ethicsinfotech.in",
    'depends': ['sales_team', 'account'],

    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/ethics_amc_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'price': 10,
    'currency': 'USD',
    'support': 'info@ethicsinfotech.in',
    'installable': True,
    'application': False,
    'auto_install': False,
}
