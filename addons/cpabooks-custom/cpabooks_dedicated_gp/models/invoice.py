from num2words import num2words

from odoo import _, api, fields, models


class InvoiceTemplates(models.Model):
    _inherit = ["account.move"]

    show_theme_color = fields.Boolean(default=0, string="Show Theme Color")

class InvoiceLineTemplates(models.Model):
    _inherit = ["account.move.line"]

    class_name=fields.Many2one('product.class',string="Class",compute="set_class",readonly=False,store=True)

    @api.depends('product_id')
    def set_class(self):
        for rec in self:
            rec.class_name=rec.product_id.product_class.id