from odoo import models, fields, api
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
class AccountAccountInherit(models.Model):
    _inherit="account.account"

    create_asset = fields.Selection([('no', 'No'), ('draft', 'Create in draft'), ('validate', 'Create and validate')],  default='no')