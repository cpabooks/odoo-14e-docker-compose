from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line', 'amount_untaxed', 'amount_total')
    def compute_sale_margin(self):
        for order in self:
            margin_per = 0.0
            margin = 0.0
            cmp = 0.0
            for line in order.order_line:
                cmp += (line.purchase_price * line.product_uom_qty)
                try:
                    margin =  order.amount_total - ((line.purchase_price or line.product_id.standard_price) * line.product_uom_qty)
                    margin_per = (line.price_unit -line.purchase_price )/line.price_unit * 100
                except:
                    print(line.price_unit)

            if order.amount_total != 0:
                margin = order.amount_untaxed - cmp
                order.update({
                    'margin_custom' : (margin * 100) / order.amount_untaxed,
                    'margin_culculate' : order.amount_untaxed - cmp
                })
            else:
                order.update({
                    'margin_custom' : 0.0,
                    'margin_culculate' : 0.0
                })

    
    margin_custom = fields.Float('Margin Percent', compute='compute_sale_margin' , readonly=True)
    margin_culculate = fields.Float('Margin Amount', compute='compute_sale_margin' , readonly=True)
    



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    line_margin = fields.Float(digits='Account',store=True, readonly=True, compute='compute_sale_margin')


    @api.depends('price_unit','product_id', 'product_uom_qty', 'tax_id', 'order_id.partner_id', 'order_id.currency_id')
    def compute_sale_margin(self):
        for res in self:
            line_mrg_tot = 0
            cmp = 0.0
            cmp = ((res.purchase_price or res.product_id.standard_price) * res.product_uom_qty)
            margin = res.price_subtotal - cmp
            res.line_margin = margin


    def compute_invoice_line(self):
        res = super(SaleOrderLine, self).compute_invoice_line()
        res.update({'purchase_price':self.purchase_price})
        return res

    
