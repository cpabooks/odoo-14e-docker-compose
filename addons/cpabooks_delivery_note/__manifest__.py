# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xxx Delivery Note on Invoice",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ xxx Reports with header & Receivers Signature """,
    "description": """""",
    "depends": [
        'base','stock'
    ],
    "data": [
        'views/report_delivery_document_for_delivery_note_inherit.xml',
        'views/serial_in_delivery_slip.xml',
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
