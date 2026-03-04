# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "xxx_CPABooks Delivery Status on Invoice",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ (xxx Note: Dont Install, if this is available then unable to delete DO) Delivered Status view on Invoice & Sales """,
    "description": """Delivery Status""",
    "depends": [
        'base','stock','account','sale_stock', 'sale_management'
    ],
    "data": [
        'views/sales_views_inherit.xml',
        'views/account_move_views_inherit.xml',
        'views/account_move_form_view_inherit.xml'
    ],
    "images": [
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
