# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Account Partner Auto Reconcile",
    'category': 'Accounting/Accounting',
    'summary': """Account Partner Auto Reconcile.""",
    'version': '14.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to automatically reconcile all the customer invoices and vendor bills with just one click.""",
    'depends': ['account_reports'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/assets.xml',
    ],
    'qweb': [],
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://www.youtube.com/watch?v=spkkPDPS5Ow',
    'price': 19.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
