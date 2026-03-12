# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_detail_enable = fields.Boolean('Show Bank Details on Invoice Report', default=True)