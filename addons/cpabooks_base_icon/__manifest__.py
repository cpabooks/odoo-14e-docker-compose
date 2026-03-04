# -*- coding: utf-8 -*-
{
    'name': 'CPAbooks base icon',
    'version': '14.0.0.0.0',
    'category': 'POS',
    'summary': """ CPAbooks base icon""",
    'description': """
                    CPAbooks base icon
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'CPAbooks',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'hr_expense', 'sale', 'purchase', 'documents', 'stock', 'account_accountant', 'project'],
    'data': [
        'views/menu_icon.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
