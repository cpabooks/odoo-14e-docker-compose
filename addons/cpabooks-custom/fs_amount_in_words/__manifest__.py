# -*- coding: utf-8 -*-
{
    'name': 'Amount In Words',
    'summary': 'Application to display amount in word and print in report',
    'version': '14.0.1.1.0',
    'author':'SARL FOCUS SYSTEM.',
    'maintainer': 'SARL FOCUS SYSTEM.',
    'contributors':['contact <contact@focussystem.dz>'],
    'website': 'http://www.focussystem.dz',
    'depends': [
        'sale', 'purchase', 'account'
    ],
    'data': [
        'views/amount_word_view.xml',
	    'report/report.xml'
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.png'],
}
