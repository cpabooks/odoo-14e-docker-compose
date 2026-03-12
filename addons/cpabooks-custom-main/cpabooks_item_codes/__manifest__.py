# -*- coding: utf-8 -*-
# Part of Dipankar Sarkar ODOO Development
{
    "name": "CPAbooks Item Code",
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1",
    "category": "Tools/Sales",
    "summary": """ Item Code on view """,
    "description": """""",
    "depends": [
        'base','product','account','sale','stock'
    ],
    "data": [
        'views/item_code_product_view.xml',
        'views/item_code_product_product_view.xml',
        # 'views/invoice_sl_no_view.xml',
        # 'views/quotation_sl_no_view.xml',
        'views/item_code__on_invoice_report_inherit.xml',
        'views/item_code_on_quotation_report_inherit.xml',
        'views/inventory_report.xml',
        # 'views/report_settings.xml',
        # 'reports/report_invoice_template.xml',
        # 'reports/report_contracting_invoice_report.xml',
        # 'reports/purchase_order_template.xml',
        # 'reports/common_invoice_line_template.xml',
        # 'reports/common_quotation_line_template.xml',

    ],
    "images": [],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "0",
    "currency": "EUR"
}
