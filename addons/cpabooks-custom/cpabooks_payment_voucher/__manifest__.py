# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "CPABooks Payment Voucher",
    "summary": " Reports of Payment Voucher ",
    "description": """ Reports of Payment Voucher """,
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1.0.1",
    "category": "Tools/Sales",
    "depends": [
        'base', 'account', 'sale'
    ],
    "data": [
        # 'security/ir.model.access.csv',
        'data/payment_method_data.xml',
        'report/report_payment_receipt_templates.xml',
        'report/header_footer_less_payment_receipt_report.xml',
        'report/standard_payment_receipt_voucher.xml',
        # 'report/standard_payment_receipt_voucher_previous.xml',
        'report/report_menu.xml',
        'views/account_payment.xml',
        'views/account_move.xml',
        'views/account_payment_register_view_inherit.xml',
        'views/account_payment_method.xml',
        'views/report_voucher_view.xml',
        'views/sale_order_view.xml',
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
}
