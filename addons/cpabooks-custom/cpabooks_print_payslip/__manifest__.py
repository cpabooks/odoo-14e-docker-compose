# -*- coding: utf-8 -*-
{
    'name': 'Print Payslip - CPABooks',
    'version': '14.0.0.0.0',
    'category': 'Human Resources',
    'summary': """ Print Payslip """,
    'description': """
                    Print Payslip
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'Centrale Fillers',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'hr_payroll'],
    'data': [
        'views/report_payslip_templates_inherit.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
