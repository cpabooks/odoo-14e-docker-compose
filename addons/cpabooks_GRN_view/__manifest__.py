# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xx_CPABooks GRN on Accounting",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ GRN menu in accounting """,
    "description": """Goods Receipt Note""",
    "depends": [
        'base','stock','account',
    ],
    "data": [
        'views/delivery_slip_view.xml',
    ],
    "images": [
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
