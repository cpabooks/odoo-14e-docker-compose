from odoo import api, fields, models


class OrderLine(models.Model):
    _name = 'order.line'

    crm_id=fields.Many2one('crm.lead')
    product_id=fields.Many2one('product.product',string="Product")
    quantity=fields.Float(string="Quantity",default=1)
    price_unit=fields.Float(string="Unit Price")
    price_subtotal=fields.Monetary(string="Subtotal" , compute="set_price_subtotal")
    currency_id=fields.Many2one('res.currency')

    @api.depends('quantity','price_unit')
    def set_price_subtotal(self):
        for rec in self:
            rec.price_subtotal=rec.price_unit*rec.quantity

    @api.onchange('product_id')
    def set_price_unit(self):
        for rec in self:
            rec.price_unit=rec.product_id.lst_price