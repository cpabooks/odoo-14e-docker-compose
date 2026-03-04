# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approve_by = fields.Many2one('res.users', 'Approved By')
    prepared_by = fields.Many2one('res.users', 'Prepared By')
    stamp = fields.Binary('stamp', compute='_get_stamp')
    # note = fields.Text(default=lambda self: self.get_notes())

    # def get_notes(self):
    #     return "We hope our quotation are in line with your requirements & look forward to hear from you\n\n\n\n\nFor," + self.env.company.name

    def _get_stamp(self):
        for rec in self:
            # if rec.approve_by.user_stamp and not rec.prepared_by.user_stamp:
            #     rec.stamp = rec.approve_by.user_stamp
            #
            # elif not rec.approve_by.user_stamp and rec.prepared_by.user_stamp:
            #     rec.stamp = rec.prepared_by.user_stamp
            #
            # elif rec.prepared_by.user_stamp and rec.approve_by.user_stamp:
            #     rec.stamp = rec.approve_by.user_stamp
            rec.stamp = rec.approve_by.user_stamp or rec.prepared_by.user_stamp or False


    @api.onchange('company_id')
    def get_default_approve_and_prepared_by(self):
        for rec in self:
            last_val = self.env['sale.order'].search([], limit=1)
            if last_val:
                rec.approve_by = last_val.approve_by
                rec.prepared_by = last_val.prepared_by
            else:
                rec.approve_by = False
                rec.prepared_by = False

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','sale.order'),('company_id','=',self.env.company.id)])
        return get_signature_data
