from odoo import fields, models, api


class ResPartnerBankDetails(models.Model):
    _inherit = 'account.move'

    bank_detail_enable = fields.Boolean('Bank details on Invoice', default=True)