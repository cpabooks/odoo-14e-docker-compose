from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    currency_rate=fields.Float(related="currency_id.rate",string="Currency Rate")
    total_in_aed=fields.Monetary(compute="get_total_in_aed",string="Total In AED")
    is_proforma=fields.Boolean(string="Proforma Invoice")
    amount_due=fields.Monetary(string="Amount Due", compute="_get_due_amount")
    invoiced_amount = fields.Monetary('Invoiced Amount', currency_field='currency_id')
    paid_amount = fields.Monetary('Paid Amount', currency_field='currency_id')
    due_amount = fields.Monetary('Due Amount', currency_field='currency_id', compute='_compute_due_amount', store=True)

    @api.depends('amount_total', 'paid_amount')
    def _compute_due_amount(self):
        for rec in self:
            rec.due_amount = rec.amount_total - rec.paid_amount

    def action_compute_inv_pay_amt(self):
        """Compute amounts for all confirmed sale orders"""
        sales = self.env['sale.order'].search([('state', '=', 'sale'), ('company_id', '=', self.env.company.id)])

        for sale in sales:
            total_invoiced = sum(sale.invoice_ids.mapped('amount_total'))
            sale.invoiced_amount = total_invoiced

            total_paid = 0
            for inv in sale.invoice_ids:
                pay_term_lines = inv.line_ids.filtered(
                    lambda line: line.account_internal_type in ('receivable', 'payable')
                )

                invoice_partials = []
                for partial in pay_term_lines.matched_debit_ids:
                    invoice_partials.append(partial.debit_move_id.payment_id.id)
                for partial in pay_term_lines.matched_credit_ids:
                    invoice_partials.append(partial.credit_move_id.payment_id.id)

                total_paid += sum(
                    self.env['account.payment'].sudo()
                    .browse(invoice_partials)
                    .mapped('amount')
                )
            if not total_paid:
                payments = self.env['account.payment'].search([
                    ('so_id', '=', sale.id),
                    ('state', '=', 'posted')
                ])
                total_paid = sum(payments.mapped('amount'))
            sale.paid_amount = total_paid
            sale.due_amount = total_invoiced - total_paid

        # Return an action or notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Computed amounts for {len(sales)} sale orders',
                'type': 'success',
                'sticky': False,
            }
        }



    def get_total_in_aed(self):
        for rec in self:
            rec.total_in_aed=rec.amount_total/rec.currency_rate

    def action_proforma(self):
        for rec in self:
            rec.is_proforma=True

    @api.depends('order_line.invoice_lines')
    def _get_due_amount(self):
        for order in self:
            if order.order_line.invoice_lines:
                order.update({
                    'amount_due': sum(
                        order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type == 'out_invoice').mapped(
                            'amount_residual_signed')) - sum(
                        order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type == 'out_refund').mapped(
                            'amount_residual_signed'))
                })
            else:
                order.update({
                    'amount_due':order.amount_total
                })