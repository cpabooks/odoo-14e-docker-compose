# -*- coding: utf-8 -*-

{
    'name': 'Cost Estimation for Material, Labour and Overheads',
    'version': '1.0.1',
    'category': 'Project',
    'summary': 'This apps helps to calculate Job Estimation for Materials, Labours and Overheads',
    'description': """
        Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads""",
    'author': 'Lebowski',
    'depends': ['sale_management', 'sale_stock', 'hr_timesheet', 'project', 'account', 'mail', 'crm' ,'sale','sale_crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/estimation_reports.xml',
        'report/estimation_template_common.xml',
        'report/estimation_template_default.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/job_estimate_view.xml',
        'views/sale_order_view.xml',
        'views/crm_lead.xml',
        # 'views/crm_lead_views.xml',
    ],
    "images": ['images/thumbnail.gif'],
    "price": 34.99,
    "currency": 'USD',
    'installable': True,
    'auto_install': False,

}
