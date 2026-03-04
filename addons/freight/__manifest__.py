# -*- coding: utf-8 -*-
###################################################################################
#
#    Eagle ERP Software.
#    <https://www.eagle-erp.com>
#
###################################################################################
{
    'name': 'Eagle Freight Management',
    'version': '14.0.1.0.1',
    'category': 'freight',
    'price': 200.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website':'https://www.eagle-erp.com',
    'images': ['static/description/banner.jpg'],
    'author':'Ealge ERP',
    'summary': 'Eagle Freight Management',
    'description': """
Key Features
------------
* Eagle Freight Management
        """,
    'depends': ['base',
                'base_setup',
                # 'project',
                'account',
                'product',
                'web',
                'contacts',
                'sale',
                'sale_management',
                'mail',
                'board',
                'calendar',
                'hr',
                'many2many_tags_link'],
    'data': [
        'data/freight_data.xml',
        'data/freight_container_size.xml',
        'data/freight.rate.basis.csv',
        'security/ir.model.access.csv',
        'data/freight.charge.type.csv',
        # 'data/freight.charge.csv',
        'data/freight.container.type.csv',
        'data/freight.port.csv',
        'data/freight_product.xml',
        'report/bill_of_lading.xml',
        # 'report/airway_bill.xml',
        'report/freight_invoice_report.xml',
        'report/quotation_report.xml',
        # 'report/invoice_report.xml',
        # 'views/freight_report.xml',
        # 'wizard/register_invoice_freight_view.xml',

        'views/freight_view.xml',
        'views/templates.xml',
        'views/views.xml',
        'views/freight_quotation.xml',
    ],
    'qweb': [
        # "static/src/xml/freight_dashboard.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}