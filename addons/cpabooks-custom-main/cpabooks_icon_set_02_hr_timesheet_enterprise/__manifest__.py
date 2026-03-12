# -*- coding: utf-8 -*-
{
    'name': 'cpabooks icon set 02 hr timesheet enterprise',
    'version': '14.0.0.0.0',
    'category': 'Extra Tools',
    'summary': """ CPAbooks icon set 02_hr_timesheet""",
    'description': """
                    CPAbooks icon set 02_hr_timesheet
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'CPAbooks',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'hr_timesheet', 'bi_employee_payslip_report', 'cpabooks_hr_allowance', 'cpabooks_hr_extend',
                'cpabooks_hr_payroll'],
    'data': [
        'views/menu_icon.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
