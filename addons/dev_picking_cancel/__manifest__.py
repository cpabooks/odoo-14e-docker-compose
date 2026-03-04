# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    'name': 'xxx_(scrap) All in one Cancel Sale,Purchase,Picking', 
    'version': '14.0.1.0',
    'author': 'Eagle ERP',
    'sequence': 1,
    'category': 'Warehouse', 
    'description':  
        """ 
        odoo App will allow to cancel sale,purchase,picking,invoice in done state in single click
    """,
    'summary': 'all in one cancel order| cancel picking',
    'depends': ['stock','sale_stock','purchase','sale'],
    "data": [
        "security/security.xml",
	"security/ir.model.access.csv",
        "views/stock_view.xml",
        "wizard/bulk_cancel_picking_views.xml",
        "wizard/bulk_set_to_draft.xml",
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

