from odoo import fields, models, api


class ResPartnerBankDetails(models.Model):
    _inherit = 'res.company'

    bank_details_header = fields.Char(string="Bank Details", default='Bank Details')
    iban_number2 = fields.Char(string="Bank Name")
    iban_number3 = fields.Char(string="Account Number")
    iban_number = fields.Char(string="IBAN No")
    address_line_1 = fields.Char(string="Address Line 1")
    address_line_2 = fields.Char(string="Address Line 2", default='Branch')
