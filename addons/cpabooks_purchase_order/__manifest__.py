# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "CPAbooks Purchase Order",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ PO with Serial & Signature """,
    "description": """""",
    "depends": [
        'base', 'purchase'
    ],
    "data": [
        'views/purchase_order_report_inherit.xml',
        'views/po_signature_line_no_view.xml',
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
