# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    num_word = fields.Char(string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount_total))


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    num_word = fields.Char(string="This purchase order form is approved for the sum of: ", compute='_compute_amount_in_word')

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for purchase in self:
            purchase.num_word = ''
            if purchase.currency_id:
                purchase.num_word = str(purchase.currency_id.amount_to_text(purchase.amount_total))


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_amount_format(self):
       for rec in self:
           currency_id = self.env.company.currency_id
           languages = self.env['res.lang'].search([])
           for lang in languages:
               if currency_id.name.lower() == 'inr':
                   rec.format_lang = '[3,2,-1]'
                   lang.grouping = '[3,2,-1]'
               else:
                   rec.format_lang = '[3,0]'
                   lang.grouping = '[3,0]'
    num_word = fields.Char(string="This invoice is approved for the sum of: ", compute='_compute_amount_in_word')
    format_lang = fields.Char('Format', compute=_compute_amount_format)

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for invoice in self:
            invoice.num_word = ''
            if invoice.currency_id:
                invoice.num_word = str(invoice.currency_id.amount_to_text(invoice.amount_total))



