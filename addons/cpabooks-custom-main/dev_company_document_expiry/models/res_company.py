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


class res_partner(models.Model):
    _inherit = 'res.company'

    def count_current_documents(self):
        for company in self:
            company.documents = len(company.company_document_ids)

    def action_view_company_documents(self):
        documents = len(self.company_document_ids)
        if documents == 1:
            form_view = self.env.ref(
                'dev_company_document_expiry.form_dev_company_document')
            return {
                'name': 'Document',
                'res_model': 'dev.company.document',
                'res_id': self.company_document_ids.ids[0],
                'views': [(form_view.id, 'form')],
                'type': 'ir.actions.act_window',
            }
        elif documents > 1:
            tree_view_id = self.env.ref(
                'dev_company_document_expiry.tree_dev_company_document')
            form_view = self.env.ref(
                'dev_company_document_expiry.form_dev_company_document')
            return {
                'name': 'Documents',
                'res_model': 'dev.company.document',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id.id, 'tree'), (form_view.id, 'form')],
                'domain': [('id', 'in', self.company_document_ids.ids)],
            }
        else:
            return True

    company_document_ids = fields.One2many("dev.company.document",
                                            "many_compnay_id", string="Documents")
    documents = fields.Integer(compute="count_current_documents")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
