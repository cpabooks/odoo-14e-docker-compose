from odoo import api, fields, models, tools, _


class MaterialEstimate(models.Model):
    _inherit = "material.estimate"

    profit_per=fields.Float(string="Profit %")
    profit_amount=fields.Float()
    overhead_per=fields.Float(string="Overhead %")
    overhead_amount=fields.Float()
    discount_amount=fields.Float()

    @api.onchange('profit_per','overhead_per',"discount")
    def compute_amount(self):
        for rec in self:
            rec.profit_amount=(rec.quantity * rec.price_unit)*(rec.profit_per/100)
            rec.overhead_amount=(rec.quantity * rec.price_unit)*(rec.overhead_per/100)
            before_discount=(rec.quantity * rec.price_unit)+rec.profit_amount+rec.overhead_amount
            rec.discount_amount=(before_discount * (rec.discount or 0.0) / 100.0)
            after_discount=before_discount - (before_discount * (
                    rec.discount or 0.0) / 100.0)
            rec.subtotal = after_discount

    @api.onchange('quantity', 'price_unit', 'discount')
    def onchange_quantity(self):
        for rec in self:
            rec.profit_amount = (rec.quantity * rec.price_unit) * (rec.profit_per / 100)
            rec.overhead_amount = (rec.quantity * rec.price_unit) * (rec.overhead_per / 100)
            before_discount = (rec.quantity * rec.price_unit) + rec.profit_amount + rec.overhead_amount
            rec.discount_amount = (before_discount * (rec.discount or 0.0) / 100.0)
            after_discount = before_discount - (before_discount * (
                    rec.discount or 0.0) / 100.0)
            rec.subtotal = after_discount

