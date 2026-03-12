from num2words import num2words

from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_class=fields.Many2one("product.class", string="Class")
    prod_description=fields.Char(string="Product Description")
    prod_inspiration=fields.Char(string="Product Inspiration")


