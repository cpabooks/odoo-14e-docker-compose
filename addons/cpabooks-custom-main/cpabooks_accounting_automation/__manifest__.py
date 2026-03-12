# -*- coding: utf-8 -*-
{
    'name': "CPABooks Accounting Automation",
    'summary': " CPABooks Accounting Automation ",
    'description': """
        CPABooks Accounting Automation 1) Date Formate
    """,
    'author': "CPABooks",
    'website': "http://www.odoo.com",
    'category': 'Accounting',
    'version': '14.0.1.0.0',
    'depends': [
        'base','account', 'CPAbooks_db_lock', 'mail'
    ],
    'data': [
        'views/account_payment_inherit.xml',
        'views/account_move_inherit.xml',
        'views/account_journal_inherit.xml',
        'views/language_form_inherit.xml',
        # 'views/hide_default_modules.xml',
        # 'report/payment_receipt_report_inherit.xml',
        # 'report/report_invoice_template.xml',
        'views/delete_documents_internal_files.xml',
        'views/payment_receipt_voucher.xml',
        # 'views/base_document_layout_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
