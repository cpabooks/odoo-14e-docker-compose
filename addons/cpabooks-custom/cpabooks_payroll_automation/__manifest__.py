# -*- coding: utf-8 -*-
{
    'name': 'CPAbooks Payroll Automation',
    'version': '14.0.0.0.0',
    'category': 'Project',
    'summary': """ Job order extend """,
    'description': """
                    CPABooks Payroll Automation
                    """,
    'author': 'CPAbooks, Kamrul Hasan',
    'website': "https://www.cpabooks.org/",
    'company': 'CPABooks',
    'maintainer': 'cpabooks, Kamrul Hasan',
    'depends': ['base', 'hr_payroll', 'cpabooks_hr_extend', 'cpabooks_hr_payroll', 'cpabooks_payroll_overtime',
                'cpabooks_hr_allowance', 'cpabooks_print_payslip', 'bi_hr_overtime_request', 'eq_payslip_payment',
                'bi_employee_advance_salary'],
    'data': [
        'security/ir.model.access.csv',
        'data/resource_calendar.xml',
        'data/hr_payroll_structure_type.xml',
        'data/hr_payroll_structure.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_salary_rule.xml',
        'data/update_salary_rules_debit_credit.xml',
        'views/hr_payslip_by_employees.xml',
        'views/salary_python_code_setup.xml',
        'views/hr_employee.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
