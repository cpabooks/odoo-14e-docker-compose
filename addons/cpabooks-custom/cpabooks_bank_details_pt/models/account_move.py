# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_detail_enable = fields.Boolean('Show Bank Details on Invoice Report', default=True)

    def _check_isntallation(self):
        for rec in self:
            is_module_install=self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_digital_signature_pt')])
            return True if is_module_install else False