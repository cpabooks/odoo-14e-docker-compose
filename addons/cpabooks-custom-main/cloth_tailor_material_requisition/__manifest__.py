# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tailor Cloth Request',
    'version': '1.2.1',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Material/Purchase Requisition for Cloth Request by Employee.""",
    'description': """
This module allowed you to create Material/Purchase Requisition From Cloth Request.
cloth 
cloth request
Purchase Requisitions
material Purchase Requisitions
material Purchase Requisition
cloth
cloth management

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://youtu.be/8yBdQ1NN9LU',
    'category': 'Warehouse',
    'depends': [
        'material_purchase_requisitions',
        'cloth_tailor_management_odoo'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cloth_request_material_requisition_view.xml',
        'wizard/work_order_requisition_view.xml',
        'views/cloth_request_view.xml',
        'views/workorder_view.xml',
        'views/purchase_requisitions_view.xml'
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
