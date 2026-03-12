# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    enquiry_number = fields.Char(string='Enquiry Number')
    subject = fields.Char(string='Subject')
    attention = fields.Char(string='Attention')
    delivery_detail = fields.Char(string='Delivery')
    make_detail = fields.Char(string='Make')
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')

    def get_t_and_c_cp(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
        if get_model:
            get_field = self.env['ir.model.fields'].sudo().search(
                [('name', '=', "t_and_c"), ('model_id', '=', get_model.id)])

            if get_field and self.show_t_and_c:
                return self.t_and_c
            else:
                return []

    def get_warm_regards_cp(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
        if get_model:
            get_field = self.env['ir.model.fields'].sudo().search(
                [('name', '=', "warm_regards"), ('model_id', '=', get_model.id)])

            if get_field and self.show_warm_regards:
                return self.warm_regards
            else:
                return []

    def is_html_empty(self, html_content):
        """Check if a html content is empty. If there are only formatting tags or
        a void content return True. Famous use case if a '<p><br></p>' added by
        some web editor.

        :param str html_content: html content, coming from example from an HTML field
        :returns: bool, True if no content found or if containing only void formatting tags
        """
        if not html_content:
            return True
        tag_re = re.compile(r'\<\s*\/?(?:p|div|span|br|b|i)\s*/?\s*\>')
        return not bool(re.sub(tag_re, '', html_content).strip())


    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount_total))

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.delivery_detail:
            invoice_vals['delivery_detail'] = self.delivery_detail
        if self.make_detail:
            invoice_vals['make_detail'] = self.make_detail
        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # description_field = fields.Html(string="Plan Description")