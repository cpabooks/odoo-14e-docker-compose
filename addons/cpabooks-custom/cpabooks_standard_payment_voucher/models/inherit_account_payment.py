from odoo import fields, models, api
class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    num_word = fields.Char(string="Payment In Word: ", compute='_compute_amount_in_word')

    @api.depends('amount')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount))

    def get_signature(self):
        get_model=self.env['ir.model'].sudo().search([('model','=','signature.setup')])
        if get_model:
            get_signature_data=self.env['signature.setup'].search([('model','=','account.payment'),('company_id','=',self.env.company.id)])
            return  get_signature_data
        else:
            return []

    def get_signature_standard(self):
        get_model=self.env['ir.model'].sudo().search([('model','=','signature.setup')])
        if get_model:
            get_signature_data=self.env['signature.setup'].search([('model','=','account.payment'),('company_id','=',self.env.company.id)])
            return  get_signature_data
        else:
            return []

