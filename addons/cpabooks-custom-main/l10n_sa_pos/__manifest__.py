# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'K.S.A. - Point of Sale',
    'author': 'Eagle ERP',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """
K.S.A. POS Localization
=======================================================
    """,
    'license': 'LGPL-3',
    'depends': ['l10n_gcc_pos', 'l10n_sa_invoice'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'auto_install': True,
}
