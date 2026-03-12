from odoo import api, models, fields, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    so_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        domain="[('partner_id', '=', partner_id), ('due_amount', '>', 0)]"
    )
    signatory_id = fields.Many2one(
        'res.users',
        string='Signatory',
        default=lambda self: self.env.user
    )

    @api.onchange('so_id')
    def _onchange_so_id(self):
        if self.so_id:
            self.amount = self.so_id.due_amount