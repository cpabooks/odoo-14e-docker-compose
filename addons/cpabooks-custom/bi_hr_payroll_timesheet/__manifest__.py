# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Payslip based on Timesheet Activity(Hourly)',
    'version': '14.0.0.0',
    'category': 'Human Resources',
    'sequence': 2,
    'summary': 'Apps uses employee payslip based on timesheet activities hourly base payslip salary slip based on timesheet employe hourly payslip from timesheet employee timesheet sheet calculate hourly payslip hourly payroll for employee hourly payroll from timesheet',
    'description': """

    odoo employee timesheet payslip employee playslip hourly bill payslip bill timesheet logged hours reports in timesheet 
    Odoo Hourly payslip on Payroll HR hourly payroll payslip based on hourly timesheet payslip intergrated with timesheet. 
    Odoo hourly salary calculation for employee payslip calculation based on timesheet activity HR timesheet payroll
    Odoo Hourly payslip for employee,Generate Employee payslip based on timesheet job contract job contracting construction job 
    Odoo contracting job contract estimation cost estimation project estimation
    odoo hourly payroll for employee hourly payroll management odoo payslip from timesheet payroll from timesheet
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
""",
    'author': 'BrowseInfo',
    'price': 20,
    'currency': "EUR",
    'website': 'https://www.browseinfo.in',
   
    'depends': [
        'hr_payroll','hr_timesheet',
    ],
    'data': [
       
        'views/hr_contract_view.xml',
          

    ],
    'demo': [
    ],
    'test': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
    'live_test_url':'https://youtu.be/ml6khb-yxsw',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
