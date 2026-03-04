# -*- coding: utf-8 -*-
{
    "name": "xxCPAbooks Delivery Slip",
    "summary": " Delivery Slip Report Customization ",
    "description": """ Delivery Slip Report Customization """,
    "author": "Dipankar Sarkar",
    "support": "dipankar.sarkar.bubt@gmail.com",
    "version": "14.0.1.0.0",
    "category": "Tools/Sales",
    "depends": [
        'base', 'stock', 'sale_stock','account','stock_landed_costs'
    ],
    "data": [
        'views/stock_picking_views.xml',
        'report/report_deliveryslip.xml',
        'report/headerless_delivery_report.xml',
        'report/report_menu.xml',
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
}
