# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "CPABooks Delivery Note Payment Voucher PO Report",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ Reports with header & Receivers Signature """,
    "description": """""",
    "depends": [
        'base','sale_management','delivery','account'
    ],
    "data": [
        'views/delivery_slip_report_inherit_view.xml',
        'views/payment_voucher_report_inherit_view.xml',
        'views/purchase_order_report_inherit_view.xml',
        'views/item_code_invoice_report.xml',
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
