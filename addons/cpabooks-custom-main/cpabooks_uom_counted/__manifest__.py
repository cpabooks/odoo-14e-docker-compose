# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xx_CPABooks another UoM counted",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ Reports with header & Receivers Signature """,
    "description": """""",
    "depends": [
        'base','uom','sale','purchase'
    ],
    "data": [
        'views/another_uom_counted_view.xml',
        'views/quotation_report_uom_inherit.xml',
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
