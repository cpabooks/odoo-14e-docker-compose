from odoo import fields, models, api

class ItemonProduct(models.Model):
    _inherit = 'product.template'

    item_code = fields.Char(string='Item Code')
    default_code = fields.Char('Part Number', index=True)