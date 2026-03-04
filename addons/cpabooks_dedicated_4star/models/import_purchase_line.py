from odoo import api, models, fields, _
from odoo.fields import Many2one


class ImportPurchaseLine(models.Model):
    _name = 'import.purchase.line'
    _description = 'Import Purchase Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    order_id = fields.Many2one('purchase.order', 'Purchase')
    fr_currency_id = fields.Many2one('res.currency', string='Fr Currency', compute='_get_fr_currency_id', store=True,
                                     readonly=False)
    fr_rate = fields.Float('Fr Rate', digits=(16, 5), compute='_get_fr_currency_rate', store=True, readonly=False)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    name = fields.Text('Description', compute='_get_product_description')
    product_qty = fields.Float('Quantity', digits=(16, 5))
    fr_price_unit = fields.Float('Unit Price', digits=(16, 5), store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='order_id.currency_id', store=True)
    amount = fields.Float('Amount', digits=(16, 5), compute='_compute_amount', store=True)
    amount_in_aed = fields.Float('Amount in AED', digits=(16, 5), store=True, compute='_compute_amount_in_aed')

    @api.model
    def create(self, vals):
        res = super(ImportPurchaseLine, self).create(vals)
        volume = self.env['calculation.volume.line']
        weight = self.env['calculation.weight.line']
        create_vals = {
            'order_id': res.order_id.id,
            'import_id': res.id,
        }
        search_vals = [
            ('import_id', '=', res.id),
            ('company_id', '=', res.company_id.id)
        ]
        if res.order_id.calculation_type == 'by_volume':
            cal_volume_id = volume.search(search_vals, limit=1)
            if not cal_volume_id:
                volume.create(create_vals)
            else:
                volume.write(create_vals)
        else:
            cal_weight_id = weight.search(search_vals, limit=1)
            if not cal_weight_id:
                weight.create(create_vals)
            else:
                weight.write(create_vals)
        return res

    @api.model
    def unlink(self):
        cr = self.env.cr
        volume = self.env['calculation.volume.line']
        weight = self.env['calculation.weight.line']
        for rec in self:
            search_vals = [
                ('import_id', '=', rec.id),
                ('company_id', '=', rec.company_id.id)
            ]
            volume_id = volume.search(search_vals, limit=1)
            if volume_id:
                volume_id.unlink()
                cr.commit()

            weight_id = weight.search(search_vals, limit=1)
            if weight_id:
                weight_id.unlink()
                cr.commit()
        return super(ImportPurchaseLine, self).unlink()

    @api.depends('product_id')
    def _get_product_description(self):
        """Get product Description"""
        for rec in self:
            rec.name = f"{rec.product_id.name}\n{rec.product_id.prod_description if rec.product_id.prod_description else ''}" if rec.product_id else ''

    @api.depends('product_qty', 'fr_price_unit')
    def _compute_amount(self):
        """Calculate total amount (amount field)"""
        for rec in self:
            rec.amount = rec.product_qty * rec.fr_price_unit

    @api.depends('fr_rate', 'amount')
    def _compute_amount_in_aed(self):
        """Calculate amount in aed"""
        for rec in self:
            rec.amount_in_aed = rec.amount * rec.fr_rate

    @api.depends('order_id', 'order_id.fr_currency_id')
    def _get_fr_currency_id(self):
        """Get Foreign currency id from parent"""
        for rec in self:
            rec.fr_currency_id = rec.order_id.fr_currency_id.id if rec.order_id and rec.order_id.fr_currency_id else False

    @api.depends('fr_currency_id')
    def _get_fr_currency_rate(self):
        """Get Foreign Currency Rate from foreign currency id"""
        for rec in self:
            rec.fr_rate = rec.fr_currency_id.rate
