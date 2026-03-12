from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    import_purchase_line = fields.One2many('import.purchase.line', 'order_id', 'Import Purchase')
    fr_currency_id = fields.Many2one('res.currency', 'Fr Currency')
    # fr_currency_rate = fields.Float('Fr Rate In Local')
    landed_cost_input_line = fields.One2many('landed.cost.line', 'order_id', 'Landed Cost Input')
    calculation_volume_line = fields.One2many('calculation.volume.line', 'order_id', 'Calculation By Volume')
    calculation_weight_line = fields.One2many('calculation.weight.line', 'order_id', 'Calculation by Weight')
    calculation_type = fields.Selection([
        ('by_volume', 'By Volume'),
        ('by_weight', 'By Weight')
    ], 'Calculation Type', default='by_volume')
    purchase_type = fields.Selection([
        ('local', 'Local'),
        ('import', 'Import')
    ], 'Purchase Type', default='local', readonly=True)
    landed_invoice_count = fields.Integer('Landed Cost Bills', compute='_compute_landed_cost_bills', default=0.0)
    cal_vol_ids = fields.One2many('cal.vol.line', 'order_id', 'Calc Vol Line')
    calc_weight_ids = fields.One2many('calc.weight.line', 'order_id', 'Calc Wight Line')

    def _get_unit_price(self, import_id=False):
        """Get Final Unit price in AED from calculation line depending on calculation type.
        If calculation type is 'by_volume' thant get value form calculation volume line or else
        get value form calculation weight line"""
        if not import_id:
            return 0.0
        amount = 0.0
        try:
            if self.calculation_type == 'by_volume':
                line = self.env['calculation.volume.line'].search([
                    ('import_id', '=', import_id.id),
                    ('order_id', '=', self.id)
                ], limit=1)
                amount = line.price_unit_final_aed
            elif self.calculation_type == 'by_weight':
                line = self.env['calculation.weight.line'].search([
                    ('import_id', '=', import_id.id),
                    ('order_id', '=', self.id)
                ], limit=1)
                amount = line.final_unit_price
            return amount
        except Exception as e:
            print(e)
            return 0.0

    def action_final_import_purchase(self):
        """Create final purchase from import purchase calculations."""
        self.ensure_one()
        order_line = self.env['purchase.order.line']
        if self.import_purchase_line:
            for import_id in self.import_purchase_line:
                price_unit = self._get_unit_price(import_id)
                print(price_unit)
                vals = {
                    'import_id': import_id.id,
                    'order_id': self.id,
                    'product_id': import_id.product_id.id,
                    'price_unit': price_unit,
                    'product_qty': import_id.product_qty
                }
                existing = order_line.search([
                    ('import_id', '=', import_id.id),
                    ('order_id', '=', self.id)
                ], limit=1)
                if not existing:
                    order_line.create(vals)
                else:
                    existing.write(vals)

    def action_create_landed_cost_bills(self):
        """Create vendor bills for each partner with corresponding landed cost lines."""
        AccountMove = self.env['account.move']  # Reference to vendor bills model
        for rec in self:
            landed_cost_partner_ids = rec.landed_cost_input_line.mapped('partner_id')
            for partner in landed_cost_partner_ids:
                # Get all landed cost lines for the current partner
                landed_cost_lines = rec.landed_cost_input_line.filtered(lambda l: l.partner_id == partner)

                if not landed_cost_lines:
                    continue  # Skip if no lines exist for the partner
                invoice_vals = rec._prepare_landed_cost_invoice(partner)
                for line in landed_cost_lines:
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
                bill = AccountMove.create(invoice_vals)
                print(bill.name)

    def _prepare_landed_cost_invoice(self, partner):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        # partner_invoice_id = line.product_id.id
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner.id,
            # 'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'import_purchase_id': self.id,
        }
        return invoice_vals

    def _compute_landed_cost_bills(self):
        for rec in self:
            lines = self.env['account.move'].search_count([
                ('import_purchase_id', '=', self.id)
            ])
            rec.landed_invoice_count = lines

    def action_view_landed_cost_invoices(self):
        action = {
            'name': 'Landed Cost Bills',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {
                'default_import_purchase_id': self.id
            }
        }
        if self.landed_invoice_count == 1:  # Ensure it's an integer comparison
            landed_bill = self.env['account.move'].search([('import_purchase_id', '=', self.id)], limit=1)
            if landed_bill:
                action.update({
                    'view_mode': 'form',
                    'res_id': landed_bill.id,
                    'view_id': self.env.ref('account.view_move_form').id,
                })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('import_purchase_id', '=', self.id)],
                'view_id': False,  # Ensures default views are used
            })

        return action

    def action_final_import_purchase_xl(self):
        self.ensure_one()
        order_line = self.env['purchase.order.line']
        existing = False
        if self.calculation_type == 'by_volume':
            vol_ids = self.env['cal.vol.line'].search([
                ('order_id', '=', self.id)
            ], order="id asc")
            for line in vol_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'taxes_id': False,
                    'order_id': self.id,
                    'vol_id': line.id
                }
                existing = order_line.search([
                    ('order_id', '=', self.id),
                    ('vol_id', '=', line.id)
                ], limit=1)
                if existing:
                    existing.write(vals)
                else:
                    order_line.create(vals)

        elif self.calculation_type == 'by_weight':
            weight_lines = self.env['calc.weight.line'].search([
                ('order_id', '=', self.id)
            ], order="id asc")
            for line in weight_lines:
                vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'taxes_id': False,
                    'order_id': self.id,
                    'weight_id': line.id
                }
                existing = order_line.search([
                    ('order_id', '=', self.id),
                    ('product_id', '=', line.product_id.id)
                ], limit=1)
                if existing:
                    existing.write(vals)
                else:
                    order_line.create(vals)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    import_id = fields.Many2one('import.purchase.line', 'Import Purchase')
    vol_id = fields.Many2one('cal.vol.line', 'Volume')
    weight_id = fields.Many2one('calc.weight.line', 'Weight')

    # prod_rate = fields.Float('Prod Rate')
    # lc_rate = fields.Float('LC Rate')
    # price_unit = fields.Float('Unit Price', digits=(16, 5))

    def _prepare_account_move_line(self):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        import_line_id = self.env['import.purchase.line'].search([
            ('id', '=', self.import_id.id)
        ], limit=1)
        try:
            unit_price = import_line_id.amount_in_aed / import_line_id.product_qty if import_line_id and import_line_id.amount_in_aed >= 1 else self.price_unit
        except Exception as e:
            _logger.error(f'Failed to calculate unit price {e}')
            unit_price = 0.0
        res.update({
            'price_unit': unit_price
        })
        return res

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()
        for rec in self:
            if rec.order_id.purchase_type == 'import':
                price_subtotal = 0
                price_unit = 0
                if rec.order_id.calculation_type == 'by_volume':
                    price_subtotal = rec.vol_id.current_rate + rec.vol_id.freight

                elif rec.order_id.calculation_type == 'by_weight':
                    price_subtotal = rec.weight_id.current_rate + rec.weight_id.freight

                try:
                    price_unit = price_subtotal / rec.product_qty
                except Exception as e:
                    _logger.error(f"Failed to calculate {e}")

                rec.write({
                    'price_subtotal': price_subtotal,
                    'price_unit': price_unit
                })
