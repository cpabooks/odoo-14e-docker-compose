from odoo import api, models, fields, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_id')
    def get_name(self):
        for rec in self:
            if rec.product_id.description:
                rec.name = f'{rec.product_id.name} \n {rec.product_id.description}'
            else:
                rec.name = f'{rec.product_id.name}'
