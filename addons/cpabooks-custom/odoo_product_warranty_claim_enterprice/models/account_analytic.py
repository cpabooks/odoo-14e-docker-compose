# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    custom_warranty_registration_ids = fields.One2many(
        'product.warranty.registration',
        'contract_id',
        string='Warranty Registration',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
