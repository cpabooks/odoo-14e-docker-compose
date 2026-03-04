# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_128 = fields.Image(string='Image', related='product_id.image_128')
