# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Meeting Minutes and Print Meeting Report',
	'summary': 'Apps Meeting Minutes Print Meeting Minutes print meetings minutes print minutes meetings print minutes of meetings print Meeting pdf report Print Meeting Minutes pdf report Minutes of meeting pdf reports allow to print Meeting Minutes Print meeting report',
	'description': """Allow you to add minutes of meetings and print pdf. """,
	'author': 'BrowseInfo',
	'website': 'https://www.browseinfo.com',
	'category': 'Extra Tools',
	'version': '14.0.0.4',
    "price": 9,
    "currency": 'EUR',
	'depends': ['base','calendar','crm', 'sh_print_lead'],
	'data': [
        'security/ir.model.access.csv',
		'views/view_meeting.xml',
		'views/meeting_list_view.xml',
		'views/crm_lead.xml',
		'report/report_meeting.xml',
		'report/report_meeting_template.xml',
		'report/crm_lead_template_inherit.xml',
		],
	'auto_install': False,
	'license': 'OPL-1',
	'installable': True,
	'application': True,
	'live_test_url' :'https://youtu.be/w5JA0Sn_8Ko',
	'qweb': [
	],
    "images":["static/description/Banner.gif"],

}

