from odoo import api, models, fields,_

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    last_depreciation_date = fields.Date('Last Recognition Date')