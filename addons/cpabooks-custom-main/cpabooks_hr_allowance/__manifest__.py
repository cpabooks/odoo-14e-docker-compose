# -*- coding: utf-8 -*-
{
    'name': 'HR Allowance',
    'version': '14.0.0.0.0',
    'category': 'Human Resources',
    'summary': """ HR Allowance """,
    'description': """
                    HR Allowance
                    """,
    'author': 'Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'Centrale Fillers',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'hr_contract','bi_hr_payroll_timesheet', 'hr_contract_salary'],
    'data': [
        'views/hr_contract.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
