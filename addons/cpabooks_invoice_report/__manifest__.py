# -*- coding: utf-8 -*-
{
    'name': 'Invoice Report ',
    'version': '1.0.1',
    'summary': 'CPA invoice report',
    'sequence': -100,
    'description': """CPA invoice report""",
    'category': 'Productivity',
    'author': 'Kamrul Hasan',
    'website': 'https://www.parimaldbz.com',
    'license': 'LGPL-3',
    'images': [],
    'depends': ['account'],
    'data': [
        'views/invoice_report_templates_inherit.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
