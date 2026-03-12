from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    image = fields.Binary(string="Image")
    image_name = fields.Char()

    @api.onchange('product_id')
    def set_image(self):
        for rec in self:
            rec.image=rec.product_id.image_1920

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        res.update({'image': self.image,
                    'image_name': self.image_name })
        return res