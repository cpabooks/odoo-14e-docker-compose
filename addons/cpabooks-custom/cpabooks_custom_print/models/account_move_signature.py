# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','account.move'),('company_id','=',self.env.company.id)])
        return  get_signature_data

    @api.model
    def get_do(self):
        if self.invoice_origin:
            get_do_all = self.env['stock.picking'].sudo().search(
                [('origin', '=', self.invoice_origin), ('state', '=', 'done')])
            get_do = ""
            for rec in get_do_all:
                get_do += rec.name + ', '
            return get_do
        else:
            get_do = []
        
