# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Product Warranty Registration & Claim for Enterprise Edition',
    'version' : '2.5',
    'depends' : [
#             'contract_recurring_invoice_analytic',
#             'website_helpdesk_support_ticket',
            'helpdesk',
            'product',
            'sale',
            'sale_subscription',
            'website'
                ],
    'price' : 199.0,
    'currency': 'EUR',
    'category': 'Sales',
    'description': """
Product Warranty Registration & Claim
Odoo Product Warranty Claim
claim
claim management
odoo claim
helpdesk
warranty_registration
ticket
support
warranty
warranty registration
Register Warranty
Warranty Renewal
claim app
claim odoo
odoo claim
warranty odoo product
product odoo warranty
customer warranty
product warranty
Product Warranty Registration, Warranty Renewal & Warranty Claim
Product Warranty Registration
Warranty Claim
Warranty Renewal
Odoo Product Warranty Claim
Product Warranty
Display Warranty Claim (qweb)
Helpdesk Support Ticket Genarate (qweb)
product.warranty.registration.form (form)
product.warranty.registration.search (search)
product.warranty.registration.tree (tree)
template_report_warranty (qweb)
template_report_warranty_data (qweb)
Product Clain
Warranty Claim
Customer Warranty
Warranty Claims
Warranty Support
Warranty Claim Request
Create Warranty Claim
Product Warranty
Warranty Report
My Warranty
Warranty Menu on Helpdesk
            """,
    'summary' : 'Product Warranty Registration and Website Claim Management and Backend for Enterprise Edition',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'live_test_url':'https://youtu.be/WpSOFj0Qpr8',
    'images': ['static/description/img1.jpg'],
    'data' : [
        'data/warranty_sequence.xml',
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/contract_view.xml',
        'views/product_warranty_form_view.xml',
        'report/product_warranty_report.xml',
        'report/customer_warranty_report.xml',
        'views/my_warranty_calim.xml',
        'views/warranty_claim_template.xml',
        'views/helpdesk_support_view.xml',
#         'views/report_helpdesk_support.xml',
        'views/sale_order_views.xml',
        'views/sale_subscription_view.xml',
        'views/support_invalid.xml',
              ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
