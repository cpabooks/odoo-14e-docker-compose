# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_disclaimer(self):
        message = "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct."
        return message or ''

    disclaimer = fields.Text(string='Disclaimer', default=_default_disclaimer)
