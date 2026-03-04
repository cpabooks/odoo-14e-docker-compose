# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    bank_detail_enable = fields.Boolean('Show Bank Details on Quotation', default=True)