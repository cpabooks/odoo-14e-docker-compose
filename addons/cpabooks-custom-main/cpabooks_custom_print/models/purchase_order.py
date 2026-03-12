# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PoTerms(models.Model):
    _name = 'po.terms'
    _description = 'Purchase Order Terms and Conditions'

    name = fields.Char(string='Name', required=True)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_note(self):
        terms_ids = self.env['po.terms'].search([])
        notes = ''
        no = 1
        if terms_ids:
            for term in terms_ids:
                notes += str(no) + '. ' + term.name + '\n'
                no += 1
        return notes

    notes = fields.Text(string='Terms and Conditions', default=_default_note)
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')

    rfq_date=fields.Datetime(related="create_date",string="RFQ Date")

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for purchase in self:
            purchase.num_word = ''
            if purchase.currency_id:
                purchase.num_word = str(purchase.currency_id.amount_to_text(purchase.amount_total))

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'dest_address_id': False,
            })
            return
        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery'])
        values = {
            # 'dest_address_id': addr['delivery'],
            'dest_address_id': False,
        }
        self.update(values)
