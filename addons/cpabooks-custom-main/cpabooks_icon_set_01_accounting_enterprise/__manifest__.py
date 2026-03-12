# -*- coding: utf-8 -*-
{
    'name': 'cpabooks icon set 01_accounting enterprise',
    'version': '14.0.0.0.0',
    'category': 'Extra Tools',
    'summary': """ accounting modules related enterprise""",
    'description': """
                   accounting modules related enterprise
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'CPAbooks',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': [
        'base',
        'cpabooks_chart_of_accounts',
        'cpabooks_project_extend',
        'cpabooks_delivery_slip',
        'cpabooks_all_cancel_extend',
        'professional_templates_v1',
        'report_pdf_options',
        'dev_invoice_multi_payment',
        'stock_no_negative',
        'ir_attachment_extend',
        'ir_attachment_s3',
        'ir_attachment_url',
    ],
    'data': [
        # 'views/menu_icon.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
