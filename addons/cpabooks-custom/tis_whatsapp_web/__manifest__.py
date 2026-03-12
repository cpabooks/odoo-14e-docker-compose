# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Whatsapp on Website',
    'version': '14.0.0.2',
    'category': 'ecommerce',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'summary': 'Start Whatsapp on website',
    'website': 'http://www.technaureus.com/',
    'price': 8,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """ 
    Start Whatsapp on website
""",
    'depends': ['website_sale'],
    'data': [
        'views/res_config_settings_view.xml',
        'views/website_templates.xml',
    ],
    'demo': [
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
