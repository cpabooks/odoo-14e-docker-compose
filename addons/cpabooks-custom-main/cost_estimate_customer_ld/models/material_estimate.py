from odoo import api, fields, models, tools, _


class MaterialEstimate(models.Model):
    _name = "material.estimate"
    _description = "Material Estimate"

    # @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id.id
                # self.price_unit = self.product_id.list_price
                rec.price_unit = rec.product_id.standard_price
                rec.description=rec.product_id.description_sale if rec.product_id.description_sale else rec.product_id.name

    @api.onchange('quantity', 'price_unit', 'discount')
    def onchange_quantity(self):
        for line in self:
            price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                    line.discount or 0.0) / 100.0
            line.subtotal = price

    product_id = fields.Many2one('product.product', 'Product', required=True)
    material_id = fields.Many2one('job.estimate', 'Raw Material')
    type = fields.Selection([('material', 'Material')], string='Type', default='material', readonly=1)
    description = fields.Text('Description')
    discount = fields.Float('Discount (%)')
    subtotal = fields.Float('Net Total')
    price_unit = fields.Float('Unit Price')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    quantity = fields.Float('Quantity', default=1)
    uom_id = fields.Many2one('uom.uom', 'Unit Of Measure')
