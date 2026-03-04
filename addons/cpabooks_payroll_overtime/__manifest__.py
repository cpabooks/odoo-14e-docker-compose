# -*- coding: utf-8 -*-
{
    'name': 'Payroll Overtime',
    'version': '1.0.1',
    'summary': 'CPA Overtime for employee',
    'sequence': -100,
    'description': """CPA Overtime for employee""",
    'category': 'Productivity',
    'website': 'https://www.cpabooks.org/',
    'license': 'LGPL-3',
    'images': [],
    'depends': ['hr_payroll', 'hr_work_entry_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_overtime_line.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
