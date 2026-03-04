from odoo import fields, models, api


class SaleOrderOptionInherit(models.Model):
    _inherit = 'sale.order.option'

    image = fields.Binary(string="Image")
    image_name = fields.Char()

    @api.onchange('product_id')
    def set_image(self):
        for rec in self:
            rec.image=rec.product_id.image_1920