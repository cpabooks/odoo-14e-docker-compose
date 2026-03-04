from odoo import api, models, fields, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    item_code = fields.Char('Item Code', compute='_compute_item_code')

    @api.depends('product_id', 'product_id.item_code')
    def _compute_item_code(self):
        for rec in self:
            rec.item_code = rec.product_id.item_code if rec.product_id else False