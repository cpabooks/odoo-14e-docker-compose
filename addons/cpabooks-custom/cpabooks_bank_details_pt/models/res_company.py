# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    bank_name = fields.Char(string="Bank Name")
    bank_account_number = fields.Char(string="Bank Account Number")
    bank_iban_number = fields.Char(string="IBAN Number")
    bank_address = fields.Char(string="Bank Address")
    bank_branch = fields.Char(string="Bank Branch")

# class DocumentLayout(models.TransientModel):
#     _inherit = 'base.document.layout'
