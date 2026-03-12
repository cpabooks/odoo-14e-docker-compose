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


class dev_employee_document(models.Model):
    _inherit = 'hr.employee'

    def count_current_documents(self):
        for employee in self:
            employee.documents = len(employee.employee_document_ids)

    def action_view_employee_documents(self):
        documents = len(self.employee_document_ids)
        if documents == 1:
            form_view = self.env.ref(
                'dev_employee_document_expiry.form_dev_employee_document')
            return {
                'name': 'Document',
                'res_model': 'dev.employee.document',
                'res_id': self.employee_document_ids.ids[0],
                'views': [(form_view.id, 'form')],
                'type': 'ir.actions.act_window',
            }
        elif documents > 1:
            tree_view_id = self.env.ref(
                'dev_employee_document_expiry.tree_dev_employee_document')
            form_view = self.env.ref(
                'dev_employee_document_expiry.form_dev_employee_document')
            return {
                'name': 'Documents',
                'res_model': 'dev.employee.document',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id.id, 'tree'), (form_view.id, 'form')],
                'domain': [('id', 'in', self.employee_document_ids.ids)],
            }
        else:
            return True

    employee_document_ids = fields.One2many("dev.employee.document",
                                            "employee_id", string="Documents")
    documents = fields.Integer(compute="count_current_documents")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
