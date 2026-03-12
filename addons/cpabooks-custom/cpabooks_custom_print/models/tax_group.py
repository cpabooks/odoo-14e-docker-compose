from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class TaxGroupInherit(models.Model):
    _inherit="account.tax.group"

    @api.model
    def action_update(self):
        get_all_tax=self.env['account.tax.group'].sudo().search([('name','ilike','Tax%')])
        for rec in get_all_tax:
            rec.name=rec.name.replace('Tax','Vat')