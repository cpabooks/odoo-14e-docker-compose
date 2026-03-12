
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    Globalteckz                                                              #
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)        #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################


{
    'name': 'All in one Whatsup app Odoo integration',
    'version': '1.0',
    'category': 'Generic Modules',
    'sequence': 1,
    "summary":"All in one Whatsup integration",
    'website': '',
    'live_test_url': '',
    "author" : "Globalteckz",
	"license" : "Other proprietary",
    'images': ['static/description/Banner.png'],
    "price": "35.00",
    "currency": "USD",
    'description': """
        Odoo whatsapp connector
        whats app Odoo connection
    """,
    'depends': [
        'base','sale','mail','contacts'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'views/whatsapp_invoice_view.xml',
        'wizard/wizard_view.xml',
        'reports/SO_common_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
