from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class LabourEstimate(models.Model):
    _name = "labour.estimate"
    _description = "Labour Estimate"

    # @api.one
    @api.constrains('hours')
    def _check_hours(self):
        for rec in self:
            if rec.hours <= 0.0:
                raise UserError(_('Working hours should not be zero or negative.'))

    # @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.list_price

    @api.onchange('hours', 'price_unit', 'discount')
    def onchange_quantity(self):
        for line in self:
            price = (line.hours * line.price_unit) - (line.hours * line.price_unit) * (
                    line.discount or 0.0) / 100.0
            line.subtotal = price

    labour_id = fields.Many2one('job.estimate', 'Labour')
    type = fields.Selection([('labour', 'Labour')], string='Type', default='labour', readonly=1)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    description = fields.Text('Description')
    quantity = fields.Float('Quantity', default=1)
    subtotal = fields.Float('Sub Total')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    uom_id = fields.Many2one('uom.uom', 'Unit Of Measure')
    price_unit = fields.Float('Unit Price')
    discount = fields.Float('Discount (%)')
    hours = fields.Float('Hours', digits=(2, 2))
