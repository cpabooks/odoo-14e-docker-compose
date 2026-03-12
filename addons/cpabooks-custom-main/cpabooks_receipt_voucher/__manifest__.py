# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xxx CPABooks Receipt Voucher",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1.0.1",
    "category": "Tools/Sales",
    "summary": """ X Reports with Receipts Signature """,
    "description": """""",
    "depends": [
        'base', 'account'
    ],
    "data": [
        'report/receipt_voucher_report_inherit_view.xml',
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
}
