from odoo import api, fields, models, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    narration = fields.Text('Narration')
    # payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
    cheque_no = fields.Char(string="Cheque or Ref No.")
    cheque_date = fields.Date(string="Cheque Deposit Date")

    @api.model
    def default_get(self, fields_list):
        res = super(AccountPayment, self).default_get(fields_list)
        context = dict(self.env.context)
        if context.get('narration'):
            res.update({
                'narration': context.get('narration')
            })
        return res

    def action_view_relavent_payment(self):
        pass