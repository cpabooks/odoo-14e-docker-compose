from odoo import api, models , fields, _

class CalVolXL(models.Model):
    _name = 'cal.vol.line'
    _description = 'Calculation by volume with xl'

    order_id = fields.Many2one('purchase.order', 'Order')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float('QTY')
    fr_rate = fields.Float('Fr Rate')
    sub_total = fields.Float('Total',default=0.0, compute='_compute_sub_total')
    conv_rate = fields.Float('Conv. Rate', (16, 8))
    current_rate = fields.Float('AED', default=0.0, compute='_compute_current_rate')
    cbm_per_unit = fields.Float('CBM/Unit', default=0.0, compute='_compute_cbm_per_unit')
    total_cbm = fields.Float('Total CBM')
    freight = fields.Float('Freight', default=0.0, compute='_compute_freight')
    prod_rate_aed = fields.Float('Cost/Unit', default=0.0, compute='_compute_prod_rate_aed')

    @api.depends('product_qty', 'fr_rate')
    def _compute_sub_total(self):
        for rec in self:
            try:
                rec.sub_total = rec.product_qty * rec.fr_rate
            except Exception as e:
                rec.sub_total = 0

    @api.depends('fr_rate', 'product_qty', 'conv_rate')
    def _compute_current_rate(self):
        for rec in self:
            try:
                rec.current_rate = rec.fr_rate * rec.product_qty * rec.conv_rate
            except Exception as e:
                rec.current_rate = 0.0

    @api.depends('total_cbm', 'product_qty')
    def _compute_cbm_per_unit(self):
        for rec in self:
            cbm_per_unit = 0.0
            try:
                cbm_per_unit = rec.total_cbm / rec.product_qty
            except Exception as e:
                cbm_per_unit = 0.0
            rec.cbm_per_unit = cbm_per_unit

    @api.depends('order_id', 'total_cbm')
    def _compute_freight(self):
        for rec in self:
            freight = 0
            if rec.order_id.landed_cost_input_line:
                total_landed_cost = sum([line.amount_in_aed for line in rec.order_id.landed_cost_input_line])
                total_cbm = sum([line.total_cbm for line in rec.order_id.cal_vol_ids])
                try:
                    freight = (total_landed_cost / total_cbm) * rec.total_cbm
                except Exception as e:
                    freight = 0.0
            rec.freight = freight

    @api.depends('product_qty', 'current_rate', 'freight')
    def _compute_prod_rate_aed(self):
        for rec in self:
            try:
                rec.prod_rate_aed = (rec.current_rate + rec.freight) / rec.product_qty
            except Exception as e:
                rec.prod_rate_aed = 0.0
