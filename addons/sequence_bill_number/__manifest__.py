# -*- coding: utf-8 -*-
{
    'name': 'Display Amount In Words in quotations, invoices and purchase orders',
    'version': '14.0.0.0',
    'author': 'Cloudroits',
    'summary': 'Display Amount In Words in quotations, invoices and purchase orders, both in forms as well as reports',
    'description': """This module displays Total Amount In Words in quotations, invoices and purchase orders, both in forms as well as reports.""",
    'category': 'Sales',
    'website': 'https://www.cloudroits.com/',
    'license': 'AGPL-3',
    'depends': ['account', 'purchase'],
    'data': [
        'views/invoice_view.xml',
    ],
    'qweb': [],
    'images': ['static/description/odoo_amount_in_words_banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}