from odoo import fields, models

class InvoiceType(models.Model):
    _name = 'invoice.type'
    _description = 'Invoice Type'

    name = fields.Char(string='Invoice Type', required=True)