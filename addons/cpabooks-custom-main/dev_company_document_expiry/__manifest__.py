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
    'name': 'Company Document and Expiry Notification',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'description':
        """
        This Module add below functionality into odoo

        1.Allows you to create document for Company
        2.Attach Company's document into Company screen
        3.User can navigate to the document through Company screen also
        4.If document's expiry date is near, then system will send notification emails to specific Company

company Document and Expiry Notification
Odoo company Document and Expiry Notification
company document notification
Odoo company document notification
company document expiry 
Odoo company document expiry
manage company Documents 
odoo manage company Documents 
Allows you to create document for company 
Odoo Allows you to create document for company 
Attach companys document into company screen
Odoo Attach companys document into company screen
If document's expiry date is near, then system will send notification 
Odoo If document's expiry date is near, then system will send notification 
partner document
Odoo partner document
Manage company document
Odoo manage company document
Manage partner document 
Odoo manage partner document
Manage partner document notification
Odoo manage partner document notification
partner Document Expiry notification
Odoo partner Documenr expiry notification
partner package
Odoo partner package
company document expiry 
Odoo company Document expiry 
company document 
Odoo company document 
Manage company document 
Odoo manage company document 
This module helps you to manage company Documents
Odoo This module helps you to manage company Documents
Allows you to create document for company 
Odoo Allows you to create document for company 
Attach company's document into company screen 
Odoo Attach company's document into company screen 
User can navigate to the document through company screen also 
Odoo User can navigate to the document through company screen also 
If document's expiry date is near, then system will send notification emails to specific company 
Odoo If document's expiry date is near, then system will send notification emails to specific company 
Create company documents 
Odoo create company documents 
Access company document 
Odoo access company document 
Access document from company's screen
Odoo Access document from company's screen
Manage company document expiry 
Odoo manage company document expiry 

    """,
    'summary': 'odoo app will manage compnay Documents & send notification before document expiry, compnay document, company document expiry, company document management, document management',
    'depends': ['sale_management', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/domain.xml',
        'views/view_com_config.xml',
        'views/sequence_company_document.xml',
        'views/view_company_document.xml',
        'views/cron_company_document_expiry_reminder.xml',
        'views/view_company_partner.xml',
        'views/dev_company_document_name.xml',
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
    'live_test_url':'https://youtu.be/S26ZugNiK2M',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
