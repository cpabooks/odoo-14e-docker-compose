from num2words import num2words

from odoo import _, api, fields, models


class InvoiceTemplates(models.Model):
    _inherit = ["account.move"]

    show_theme_color = fields.Boolean(default=0, string="Show Theme Color")

