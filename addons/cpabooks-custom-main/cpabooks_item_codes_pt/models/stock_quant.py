from odoo import models, fields, api, _


class stock(models.Model):
    _inherit = 'stock.quant'

    item_code = fields.Char(string='Item Code',related="product_id.item_code")