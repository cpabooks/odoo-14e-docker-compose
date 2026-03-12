from odoo import fields, models, api
class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"


    num_word = fields.Char(string="Payment In Word: ", compute='_compute_amount_in_word')
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', default='inbound', required=True,store=1)

    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], default='customer', tracking=True, required=True,store=1)

    receiver_id=fields.Many2one('res.users',string="Receiver",default=lambda self:self.env.user.id)
    clint_bank = fields.Char('Clink Bank Name')

    # def _get_default_receiver(self):
    #     if self.payment_type=='inbound':
    #         return self.env.user.id
    #     else:
    #         return None

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

