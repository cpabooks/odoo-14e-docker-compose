# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class QuotationInherit(models.Model):
    _inherit = "sale.order"

    manual_date = fields.Date('Create Date')