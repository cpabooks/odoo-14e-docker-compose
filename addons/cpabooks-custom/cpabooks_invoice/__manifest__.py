# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xxx_CPAbooks Invoice",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Accounts",
    "summary": """ Invoice Reports with bank details &  Signature """,
    "description": """""",
    "depends": [
        'base', 'account', 'l10n_ae'
    ],
    "data": [
        # 'views/bank_detail_company_view.xml',
        # 'views/bank_detail_enable_view.xml',
        # 'views/signature_in_invoice_report_inherit.xml',
        'views/account_move_views.xml',
        'report/report_invoice_template.xml'
    ],
    "images": [
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "0",
    "currency": "EUR"
}
