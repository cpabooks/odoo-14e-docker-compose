from odoo import models, fields, api, _

class CurrencyInherit(models.Model):
    _inherit = "res.currency"

    @api.model
    def action_change_currency_unit(self):
        get_aed_currency=self.env['res.currency'].search([('name','=','AED'),('active','=',True)],limit=1)

        if get_aed_currency:
            get_aed_currency.currency_unit_label='Dirhams'
