
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HRExpense(models.Model):
    _inherit = "hr.expense"

    def action_to_submit(self):
        for rec in self:
            rec.state='draft'

    def expense_draft(self):
        expense_ids = self.env['hr.expense'].browse(self._context.get('active_ids'))
        for expense in expense_ids:
            account_move_id = expense.sheet_id.account_move_id
            expense.sheet_id.account_move_id.with_context(force_delete=True).button_cancel()
            # move.with_context(force_delete=True).button_cancel()
            # if expense.company_id.payment_opration_type == 'draft':
            #get relatade payment
            pay_term_lines = expense.sheet_id.account_move_id.line_ids \
                .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))

            invoice_partials = []
            for partial in pay_term_lines.matched_debit_ids:
                invoice_partials.append(partial.debit_move_id.payment_id.id)
            for partial in pay_term_lines.matched_credit_ids:
                invoice_partials.append(partial.credit_move_id.payment_id.id)
            payment_ids = self.env['account.payment'].search([('id', 'in', invoice_partials)])
            #get relatade payment

            # payment_ids = self.env['account.payment'].search([('ref', 'ilike', expense.sheet_id.account_move_id.name)])
            for payment in payment_ids:
                payment.button_cancels()
                payment.action_draft()
                payment.unlink()

            expense.sheet_id.write({
                'account_move_id': None
            })
            account_move_id.with_context(force_delete=True).unlink()
            expense.sheet_id.write({
                'state': 'draft'
            })
            expense.sheet_id.unlink()
            expense.write({
                'state':'draft'
            })

    def expense_cancel(self):
        expense_ids = self.env['hr.expense'].browse(self._context.get('active_ids'))
        for expense in expense_ids:
            account_move_id=expense.sheet_id.account_move_id
            expense.sheet_id.account_move_id.with_context(force_delete=True).button_cancel()
            # if expense.company_id.payment_opration_type == 'cancel':
            # get relatade payment
            pay_term_lines = expense.sheet_id.account_move_id.line_ids \
                .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))

            invoice_partials = []
            for partial in pay_term_lines.matched_debit_ids:
                invoice_partials.append(partial.debit_move_id.payment_id.id)
            for partial in pay_term_lines.matched_credit_ids:
                invoice_partials.append(partial.credit_move_id.payment_id.id)
            payment_ids = self.env['account.payment'].search([('id', 'in', invoice_partials)])
            # get relatade payment
            # payment_ids = self.env['account.payment'].search([('ref', 'ilike', expense.sheet_id.account_move_id.name)])
            for payment in payment_ids:
                payment.button_cancels()
                payment.action_draft()
                payment.unlink()
            expense.sheet_id.write({
                'account_move_id':None
            })
            account_move_id.with_context(force_delete=True).unlink()
            expense.sheet_id.write({
                'state':'draft'
            })
            expense.sheet_id.unlink()
            expense.write({
                'state': 'refused'
            })

    def expense_delete(self):
        expense_ids = self.env['hr.expense'].browse(self._context.get('active_ids'))
        for expense in expense_ids:
            account_move_id = expense.sheet_id.account_move_id
            expense.sheet_id.account_move_id.with_context(force_delete=True).button_cancel()
            # if expense.company_id.payment_opration_type == 'delete':
            # get relatade payment
            pay_term_lines = expense.sheet_id.account_move_id.line_ids \
                .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))

            invoice_partials = []
            for partial in pay_term_lines.matched_debit_ids:
                invoice_partials.append(partial.debit_move_id.payment_id.id)
            for partial in pay_term_lines.matched_credit_ids:
                invoice_partials.append(partial.credit_move_id.payment_id.id)
            payment_ids = self.env['account.payment'].search([('id', 'in', invoice_partials)])
            # get relatade payment
            # payment_ids = self.env['account.payment'].search([('ref', 'ilike', expense.sheet_id.account_move_id.name)])
            for payment in payment_ids:
                payment.button_cancels()
                payment.action_draft()
                payment.unlink()

            expense.sheet_id.write({
                'account_move_id': None
            })
            account_move_id.with_context(force_delete=True).unlink()
            expense.sheet_id.write({
                'state': 'draft'
            })
            expense.sheet_id.unlink()
            expense.write({
                'state': 'draft'
            })
            expense.unlink()