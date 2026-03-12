from num2words import num2words

from odoo import _, api, fields, models


class InvoiceTemplates(models.Model):
    _inherit = ["account.move"]

    order_by=fields.Char(string="Order By")