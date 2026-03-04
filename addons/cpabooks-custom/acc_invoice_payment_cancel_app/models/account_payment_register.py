from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    is_come_from_expense=fields.Boolean()