from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)


class LandedCostLine(models.Model):
    _name = 'landed.cost.line'
    _description = 'Landed Cost Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    order_id = fields.Many2one('purchase.order', 'Purchase')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    fr_currency_id = fields.Many2one('res.currency', 'Fr Currency', default=lambda self: self.env.company.currency_id.id)
    fr_rate = fields.Float('Fr Rate', digits=(16, 5), readonly=False,
                           compute='_get_fr_currency_rate', store=True)
    product_id = fields.Many2one('product.product', 'Product/Services', domain=[('type', '=', 'service')])
    name = fields.Text('Description', )
    product_qty = fields.Float('Quantity', digits=(16, 5))
    fr_price_unit = fields.Float('Unit Price', digits=(16, 5), readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', related='order_id.currency_id', store=True)
    amount = fields.Float('Amount', digits=(16, 5), compute='_compute_amount', store=True)
    amount_in_aed = fields.Float('Amount in AED', digits=(16, 5), compute='_compute_amount_in_aed', store=True)

    @api.onchange('product_id')
    def get_product_description(rec):
        if rec.product_id:
            rec.name = f"{rec.product_id.name}\n{rec.product_id.prod_description or ''}"
        else:
            rec.name = False

    @api.depends('product_qty', 'fr_price_unit')
    def _compute_amount(self):
        """Calculate total amount (amount field)"""
        for rec in self:
            try:
                rec.amount = rec.product_qty * rec.fr_price_unit
            except Exception as e:
                _logger.error(f'Failed to calculate amount {e}')
                rec.amount = 0.0

    @api.depends('fr_rate', 'amount')
    def _compute_amount_in_aed(self):
        """Calculate amount in aed"""
        for rec in self:
            try:
                rec.amount_in_aed = rec.amount * rec.fr_rate
            except Exception as e:
                _logger.error(f'Failed to Compute Amount in AED {e}')

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

    def _prepare_account_move_line(self):
        """Prepare account move line for landed cost vendor bills."""
        self.ensure_one()
        try:
            price_unit = self.amount_in_aed / self.product_qty
        except Exception as e:
            _logger.error(f'Failed to compute Price Unit {e}')
            price_unit = 0.0
        res = {
            'product_id': self.product_id.id,
            'quantity': self.product_qty,
            'price_unit': price_unit,
        }
        return res
