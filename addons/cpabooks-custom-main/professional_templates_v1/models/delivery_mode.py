from num2words import num2words

from odoo import _, api, fields, models


class DeliveryMode(models.Model):
    _name = "delivery.mode"

    name=fields.Char()