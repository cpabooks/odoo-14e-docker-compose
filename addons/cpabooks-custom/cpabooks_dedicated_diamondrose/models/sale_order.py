from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    print_manual_quotation = fields.Boolean(string="Print Manual Quotation?")

    manual_quotation = fields.Char(string="Manual Quotation")

    multi_salesman = fields.Many2many('res.users', string="Salesman", default=lambda self: self.env.user.ids)
    multi_sales_team = fields.Many2many('crm.team', string="Sales Team",
                                        default=lambda self: self.env.user.sale_team_id.ids)

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'multi_salesman': [(6, 0,self.multi_salesman.ids)],
            'multi_sales_team': [(6, 0,self.multi_sales_team.ids)],
        }
        return invoice_vals

    def check_image_preview(self):
        show_image = False
        for val in self.order_line:
            if val.product_id.image_1920:
                show_image = True
        return show_image

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def set_description(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.prod_description:
                    rec.name=rec.product_id.prod_description

class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'multi_salesman': [(6, 0,self.multi_salesman.ids)],
            'multi_sales_team': [(6, 0,self.multi_sales_team.ids)],
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals