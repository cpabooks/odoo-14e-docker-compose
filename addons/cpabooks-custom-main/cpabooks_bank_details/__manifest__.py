# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xx_CPABooks Bank Details",
    "summary": " CPABooks Bank Details ",
    "description": """ CPABooks Bank Details """,
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1.0.1",
    "category": "Tools/Sales",
    "depends": [
        'base', 'account','sale'
    ],
    "data": [
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/sale_order.xml',
        'report/report_invoice.xml',
        # 'security/ir.model.access.csv'
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
}