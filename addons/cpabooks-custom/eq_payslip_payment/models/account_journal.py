from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
                                                domain=[('deprecated', '=', False)],
                                                help="It acts as a default account for credit amount")
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain=[('deprecated', '=', False)],
                                               help="It acts as a default account for debit amount")