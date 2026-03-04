from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class account_invoice_line(models.Model):

    _inherit = "account.move.line"

    line_margin = fields.Float(string='Margin',store=True, digits='Account',readonly=True, compute='compute_invoice_margin')
    purchase_price =  fields.Float('Cost', compute='_get_product_cost' ,digits=dp.get_precision('Product Price'))
    margin_subtotal_calc = fields.Float(string='Margin Signed', currency_field='always_set_currency_id',
        readonly=True,store=True, compute='compute_invoice_margin')

    @api.depends('product_id')
    def _get_product_cost(self):
        for n in self:
            frm_cur = self.env.company.currency_id
            to_cur = n.move_id.currency_id
            purchase_price = n.product_id.standard_price
            if n.product_id and n.product_uom_id != n.product_id.uom_id:
                purchase_price = n.product_id.uom_id._compute_price(purchase_price, n.product_uom_id)            
            price = frm_cur._convert(
                                    purchase_price, to_cur,
                                    n.move_id.company_id or self.env.company,
                                    fields.Date.today(), round=False)
            n.purchase_price =  price

    @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
                 'product_id', 'move_id.partner_id', 'move_id.currency_id')
    def compute_invoice_margin(self):
        for res in self:
            line_mrg_tot = 0
            cmp = 0.0
            cmp = ((res.purchase_price or res.product_id.standard_price) * res.quantity)
            margin = res.price_subtotal - cmp
            res.line_margin = margin
            margin_subtotal_calc = margin
            sign = res.move_id.move_type in ['in_refund', 'out_refund'] and -1 or 1
            res.margin_subtotal_calc = margin_subtotal_calc * sign


    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(account_invoice_line, self)._onchange_product_id()
        if self.product_id:
            frm_cur = self.env.company.currency_id
            to_cur = self.move_id.currency_id
            purchase_price = self.product_id.standard_price
            if self.product_uom_id != self.product_id.uom_id:
                purchase_price = self.product_id.uom_id._compute_price(purchase_price, self.product_uom_id)
            price = frm_cur._convert(
                                    purchase_price, to_cur,
                                    self.move_id.company_id or self.env.company,
                                    fields.Date.today(), round=False)   
            self.purchase_price = price
            
        return res

    
class AccountInvoice(models.Model):
    _inherit = "account.move"

    margin_custom = fields.Float('Margin Percent', compute='compute_invoice_margin')
    margin_culculate = fields.Float('Margin Amount', compute='compute_invoice_margin')
    
    @api.depends('invoice_line_ids')
    def compute_invoice_margin(self): 
        for order in self:
            line_mrg_tot = 0
            margin = 0.0
            cmp = 0.0
            for line in order.invoice_line_ids:
                cmp += (line.purchase_price * line.quantity)
                margin = line.price_subtotal - ((line.purchase_price or line.product_id.standard_price) * line.quantity)
                line_mrg_tot += margin 
            if order.amount_total != 0 and order.amount_untaxed != 0:
                order.update({
                    'margin_custom' : (line_mrg_tot * 100) / order.amount_untaxed,
                    'margin_culculate' : line_mrg_tot
                })
            else:
                order.update({
                    'margin_custom' : 0.0,
                    'margin_culculate' : 0.0
                })


