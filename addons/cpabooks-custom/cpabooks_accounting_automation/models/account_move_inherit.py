from odoo import fields, models, api, _


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    cheque_no = fields.Char(string="Cheque or Ref No.")
    cheque_date = fields.Date(string="Cheque Deposit Date")

    payment_count = fields.Integer( string='Payment Count',compute="_compute_payment_count",default=0)

    def _compute_payment_count(self):
        count=0
        for rec in self:
            # if rec.invoice_origin.startswith('S')
            # count = self.env['account.move'].search_count([('ref', '=', rec.name)])
            pay_term_lines = rec.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))

            invoice_partials = []
            for partial in pay_term_lines.matched_debit_ids:
                invoice_partials.append(partial.debit_move_id)
                # invoice_partials.append((partial, partial.credit_amount_currency, partial.debit_move_id))
            for partial in pay_term_lines.matched_credit_ids:
                invoice_partials.append(partial.credit_move_id)
                # invoice_partials.append((partial, partial.debit_amount_currency, partial.credit_move_id))
            count=len(invoice_partials)

            rec.payment_count = count

    def action_view_relavent_payment(self):
        for rec in self:
            pay_term_lines = rec.line_ids \
                .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))

            invoice_partials = []
            for partial in pay_term_lines.matched_debit_ids:
                invoice_partials.append(partial.debit_move_id.payment_id.id)
            for partial in pay_term_lines.matched_credit_ids:
                invoice_partials.append(partial.credit_move_id.payment_id.id)
            return {
                'name': _('Payments'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'views': [(self.env.ref('account.view_account_payment_tree').id, 'tree'),
                          (self.env.ref('account.view_account_payment_form').id, 'form'), (False, 'kanban')],
                'domain': [('id', 'in', invoice_partials)],
                # 'context': {'search_default_group_by_payment_method': 1}
            }

