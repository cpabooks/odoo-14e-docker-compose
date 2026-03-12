# -*- coding: utf-8 -*-
{
    'name': "cpabooks all cancel extend",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bahar",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'dev_picking_cancel',
                # 'acc_invoice_payment_cancel_app',
                'om_mass_confirm_cancel'],

    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
