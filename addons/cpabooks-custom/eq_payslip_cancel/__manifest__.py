# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Cancel Employee Payslips & Payslip Batches",
    'category': 'Payroll',
    'version': '14.0.1.0',
    'author': 'Equick ERP',
    'description': """This module allow users to cancel the payslip and payslip batches even if payslip status is done or paid
        * Users who have Cancel Payslip access they are only able to cancel.
        * When payslip cancel it will also cancel and delete the related Accounting Entry even after posted.""",
    'summary': """cancel employee payslip batches cancel payslip batches payslip cancel payslip batch cancel employee payslip done payslip cancel salary slip cancel payroll batch payroll cancel done payslip cancel paid payslip payslip after done cancel payslip after paid""",
    'depends': ['base', 'hr_payroll'],
    'price': 12,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/security.xml',
        'views/hr_payslip_view.xml'
    ],
    'live_test_url': 'https://www.youtube.com/watch?v=IAE116LI4B4',
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: