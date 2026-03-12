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


class dev_employee_document(models.Model):
    _name = 'dev.employee.document'
    _description = 'Employee Document'

    @api.model
    def create(self, vals):
        vals['document_sequence'] = \
            self.env['ir.sequence'].next_by_code('dev.employee.document') \
            or 'New'
        result = super(dev_employee_document, self).create(vals)
        return result


    def get_expiry_day(self):
        expiry_before_days = self.env['ir.config_parameter'].sudo().get_param(
            'dev_employee_document_expiry.expiry_before_days')

        return expiry_before_days

    def send_document_expiry_emails(self):
        documents = self.env['dev.employee.document'].search([])
        for document in documents:
            before_days = int(document.get_expiry_day())
            if before_days and before_days > 0:
                deadline_expiry = document.date_expiry
                email_date = document.date_expiry
                reminder_date = deadline_expiry - \
                                timedelta(days=before_days)
                if reminder_date == date.today():
                    subject = document.document_sequence +\
                              ": Document Expiry Notification"
                    email_body =\
                        ''' <span style='font-style: 16px;font-weight: bold;'>\
                        Dear, %s</span>''' % (document.employee_id.name) + '''\
                         <br/><br/>''' + ''' <span style='font-style: 14px;'> \
                         Document <span style='font-weight: bold;'>\
                         %s</span> will be expire on %s</span>\
                         ''' % (document.document_sequence, email_date) + '''\
                          <br/> <br/> <br/>'''
                    email_id = document.env['mail.mail'].create(
                        {'subject': subject,
                         'email_from': document.env.user.company_id.email or '',
                         'email_to': document.employee_id.work_email or '',
                         'message_type': 'email',
                         'body_html': email_body})
                    email_id.send()

    @api.depends('current_date', 'date_expiry')
    def _compute_days(self):
        for record in self:
            if record.date_expiry and record.current_date:
                delta = record.date_expiry - record.current_date
                record.days = delta.days
            else:
                record.days = 0

    name = fields.Many2one('dev.employee.document.name',required=True) #domain=lambda self:[('company_id','=',self.env.company.id)],
    document_sequence = fields.Char(readonly=True)
    document_name = fields.Char("Filename")
    document = fields.Binary(string="Document")
    employee_id = fields.Many2one("hr.employee",string="Employee",
                                  required=True)

    date_issue = fields.Date(string="Issue Date")
    date_expiry = fields.Date(string="Expiry Date")
    company_id = fields.Many2one("res.company", string="Company",
                                 default=
                                 lambda self: self.env.user.company_id or False,
                                 required=True)
    note = fields.Text()

    current_date = fields.Date(string='Today Date', default=date.today())
    days = fields.Integer('Days', compute=_compute_days)

class dev_employee_document_name(models.Model):
    _name = 'dev.employee.document.name'
    _description = 'Employee Document Name'

    name=fields.Char(string="Document Name")
    company_id=fields.Many2one('res.company',string="Company",domain=lambda self:[("id",'=',self.env.company.id)]) #changed Required


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
