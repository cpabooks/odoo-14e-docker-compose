from odoo import api, fields, models, tools, _


class OverheadEstimate(models.Model):
    _name = "overhead.estimate"
    _description = "Overhead Estimate"

    # @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.list_price

    @api.onchange('quantity', 'price_unit', 'discount')
    def _onchange_quantity(self):
        for line in self:
            price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                    line.discount or 0.0) / 100.0
            line.subtotal = price

    overhead_id = fields.Many2one('job.estimate', 'Overhead')
    type = fields.Selection([('overhead', 'Overhead')], string='Type', default='overhead', readonly=1)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    description = fields.Text('Description')
    discount = fields.Float('Discount (%)')
    subtotal = fields.Float('Sub Total')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    quantity = fields.Float('Quantity', default=1)
    uom_id = fields.Many2one('uom.uom', 'Unit Of Measure')
    price_unit = fields.Float('Unit Price')
