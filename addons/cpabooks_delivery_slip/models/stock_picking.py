# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    sender_id=fields.Many2one('res.partner',string="Sender")
    receiver_id=fields.Many2one('res.partner', string="Receiver")
    default_sender_receiver=fields.Many2many('res.partner' , compute="_get_defaults_sender_receiver")

    @api.depends('company_id')
    def _get_defaults_sender_receiver(self):
        for rec in self:
            get_so = self.env['sale.order'].sudo().search([('name', '=', rec.origin)], limit=1)
            partner_ids = get_so.partner_id.child_ids.ids
            rec.default_sender_receiver=partner_ids

    # @api.depends('origin')
    # def set_sender_receiver(self):
    #     for rec in self:
    #         get_so=self.env['sale.order'].sudo().search([('name','=',rec.origin)],limit=1)
    #         partner_ids=get_so.partner_id.child_ids.ids
    #         return {'domain':{'sender_id':[('id','in',partner_ids)],'receiver_id':[('id','in',partner_ids)]}}




    @api.model
    def _default_disclaimer(self):
        message = "1. Goods once sold, will not be returned or exchanged. \n2. Buyer must check Quantity - Quality at the time of delivery of materials."
        return message or ''



    def get_ref(self):
        for rec in self:
            get_customer_ref=self.env['sale.order'].search([('name','=',rec.origin)]).client_order_ref
            return get_customer_ref
    disclaimer = fields.Text(string='Disclaimer', default=_default_disclaimer)


    def get_signature(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'signature.setup')])
        if get_model:
            get_signature_data = self.env['signature.setup'].search(
                [('model', '=', 'stock.picking'), ('company_id', '=', self.env.company.id)])
            return get_signature_data
        else:
            return []
