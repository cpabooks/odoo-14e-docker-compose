# -*- coding: utf-8 -*-
{
    'name': 'CPAbooks POS management',
    'version': '14.0.0.0.0',
    'category': 'POS',
    'summary': """ POS management """,
    'description': """
                    POS management
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'Centrale Fillers',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config.xml',
        'security/pos_user_security.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
