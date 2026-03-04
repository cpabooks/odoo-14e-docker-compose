import re

from num2words import num2words

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = ["sale.order"]

    attention_left = fields.Boolean(default=1, string="Attention Left")
    attention_right = fields.Boolean(default=0, string="Attention Right")

    show_order_date=fields.Boolean(default=0,string="Show Order Date")
    show_expiration=fields.Boolean(default=0,string="Show Expiration")
    show_project = fields.Boolean(default=1, string="Show Project")
    show_asset_no = fields.Boolean(default=1, string="Show Asset No")
    show_greeting_note = fields.Boolean(default=1, string="Show Greeting Note")
    show_exclusion = fields.Boolean(default=1, string="Show Exclusion")
