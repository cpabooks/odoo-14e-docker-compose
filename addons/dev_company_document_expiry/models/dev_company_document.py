# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api
from datetime import timedelta, date, datetime


class dev_company_document(models.Model):
    _name = 'dev.company.document'
    _description = 'company Document'
    
    @api.model
    def create(self,vals):
        vals.update({
                    'company_sequence':self.env['ir.sequence'].next_by_code('dev.company.document') or '/'
                })
        return super(dev_company_document,self).create(vals)



    def get_expiry_day(self):
        com_expiry_before_days = self.env['ir.config_parameter'].sudo().get_param(
            'dev_company_document_expiry.com_expiry_before_days')

        return com_expiry_before_days

    def send_company_expiry_emails(self):
        companys = self.env['dev.company.document'].search([])
        for company in companys:
            before_days = int(company.get_expiry_day())
            if before_days and before_days > 0:
                deadline_expiry = \
                    datetime.strptime(str(company.date_expiry), '%Y-%m-%d').date()
                
                email_date = datetime.strptime(str(company.date_expiry),
                                               "%Y-%m-%d").strftime('%d-%m-%Y')
                reminder_date = deadline_expiry - \
                                timedelta(days=before_days)
                if reminder_date == date.today():
                    subject = company.company_sequence +\
                              ": Document Expiry Notification"
                    email_body =\
                        ''' <span style='font-style: 16px;font-weight: bold;'>\
                        Dear, %s</span>''' % (company.company_id.name) + '''\
                         <br/><br/>''' + ''' <span style='font-style: 14px;'> \
                         company <span style='font-weight: bold;'>\
                         %s</span> will be expire on %s</span>\
                         ''' % (company.company_sequence, email_date) + '''\
                          <br/> <br/> <br/>'''
                    email_id = company.env['mail.mail'].create(
                        {'subject': subject,
                         'email_from': company.env.user.company_id.email or '',
                         'email_to': company.many_compnay_id.email or '',
                         'message_type': 'email',
                         'body_html': email_body})
                    email_id.send()



    name = fields.Many2one('dev.company.document.name',domain=lambda self:[('company_id','=',self.env.company.id)],required=True)
    company_sequence = fields.Char(readonly=True)
    document = fields.Binary(string="Document", required=True)
    many_compnay_id = fields.Many2one("res.company", string="Company",
                                 required=True)
    date_issue = fields.Date(string="Issue Date", required=True)
    date_expiry = fields.Date(string="Expiry Date", required=True)
    company_id = fields.Many2one("res.company", string="Company",
                                 default=
                                 lambda self: self.env.user.company_id or False,
                                 required=True)
    note = fields.Text()
    current_date = fields.Date(string='Today Date', default=date.today())

class dev_company_document_name(models.Model):
    _name = 'dev.company.document.name'
    _description = 'Company Document Name'

    name=fields.Char(string="Document Name")
    company_id=fields.Many2one('res.company',string="Company",required=True,domain=lambda self:[("id",'=',self.env.company.id)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
