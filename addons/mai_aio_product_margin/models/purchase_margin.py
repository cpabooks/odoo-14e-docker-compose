from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line', 'order_line.product_qty', 'amount_untaxed', 'amount_total', 'order_line.product_id', 'order_line.price_unit')
    def compute_purchase_margin(self):
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
                order.margin_custom = (margin * 100) / order.amount_untaxed
                order.margin_culculate = order.amount_untaxed - cmp
            else:
                order.margin_custom =  0.0
                order.margin_culculate = 0.0

    
    margin_custom = fields.Float('Margin Percent', compute='compute_purchase_margin')
    margin_culculate = fields.Float('Margin Amount', compute='compute_purchase_margin')
    

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    line_margin = fields.Float(string='Margin', digits='Account',store=True, readonly=True, compute='compute_purchase_margin')
    purchase_price =  fields.Float('Cost', compute='_get_product_cost' ,digits=dp.get_precision('Product Price'))

    @api.depends('product_id')
    def _get_product_cost(self):
        for n in self:
            frm_cur = self.env.company.currency_id
            to_cur = n.order_id.currency_id
            purchase_price = n.product_id.standard_price
            if n.product_id and n.product_uom != n.product_id.uom_id:
                purchase_price = n.product_id.uom_id._compute_price(purchase_price, n.product_uom)            
            price = frm_cur._convert(
                                    purchase_price, to_cur,
                                    n.order_id.company_id or self.env.company,
                                    fields.Date.today(), round=False)
            n.purchase_price =  price


    @api.depends('price_unit','product_id', 'product_uom_qty', 'order_id.partner_id', 'order_id.currency_id')
    def compute_purchase_margin(self):
        for res in self:
            line_mrg_tot = 0
            cmp = 0.0
            cmp = ((res.purchase_price or res.product_id.standard_price) * res.product_uom_qty)
            margin = res.price_subtotal - cmp
            res.line_margin = margin


    def compute_purchase_line(self):
        res = super(PurchaseOrderLine, self).compute_purchase_line()
        res.update({'purchase_price':self.purchase_price})
        return res

    
