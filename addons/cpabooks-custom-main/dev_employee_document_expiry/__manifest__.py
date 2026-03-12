# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Employee Document and Expiry Notification',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        This Module add below functionality into odoo

        1.Allows you to create document for employee
        2.Attach employees document into employee screen
        3.User can navigate to the document through employee screen also
        4.If document's expiry date is near, then system will send notification emails to specific employee
 Employee Document and Expiry Notification
Odoo Employee Document and Expiry Notification
Employee document notification
Odoo employee document notification
Employee document expiry 
Odoo employee document expiry
manage Employee Documents 
odoo manage Employee Documents 
Allows you to create document for employee 
Odoo Allows you to create document for employee 
Attach employees document into employee screen
Odoo Attach employees document into employee screen
If document's expiry date is near, then system will send notification 
Odoo If document's expiry date is near, then system will send notification 
HR document
Odoo hr document
Manage employee document
Odoo manage employee document
Manage HR document 
Odoo manage HR document
Manage HR document notification
Odoo manage HR document notification
HR Document Expiry notification
Odoo HR Documenr expiry notification
HR package
Odoo HR package
    """,
    'summary': 'odoo app will manage Employee Documents & send notification before document expiry, employee document, employee document expiry, hr document, employee multiple document, document expiry notify, employee own document, document list, manage document employee',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/sequence_employee_document.xml',
        'views/view_dev_employee_document.xml',
        'views/cron_employee_document_expiry_reminder.xml',
        'views/view_hr_employee.xml',
        'views/dev_employee_doc_name.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':12.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
