from odoo import api, models, fields
from datetime import timedelta, datetime
from collections import defaultdict


class DailyTransactionReport(models.TransientModel):
    _name = 'daily.transaction.report'
    _description = 'Daily Transaction Report'

    date = fields.Date('Select Date', default=lambda self: datetime.today() - timedelta(days=1))

    def check_report(self):
        data = {
            'form': self.read()[0]
        }

        coas = self.env['account.account'].search([
            ('user_type_id.name', '=', 'Bank and Cash'),
            ('name', 'ilike', 'Cash')
        ]).ids

        if self.date:
            # Fetch invoices
            invoices = self.env['account.move'].search([
                ('invoice_date', '=', self.date),
                ('move_type', '=', 'out_invoice')
            ])
            total_invoice_amount_total_signed = sum(invoice.amount_total_signed for invoice in invoices)
            total_invoice_due_amount = sum(invoice.amount_residual for invoice in invoices)

            total_invoice_received = 0.0
            invoice_data = []
            for invoice in invoices:
                pay_term_lines = invoice.line_ids.filtered(
                    lambda line: line.account_internal_type in ('receivable', 'payable'))
                # Check for payments made by cash
                cash_payments = self.env['account.payment'].search([
                    ('date', '=', self.date),
                    ('partner_id', '=', invoice.partner_id.id),
                    ('state', '=', 'posted'),
                    ('journal_id.type', '=', 'cash')
                ])

                received_amount = sum(payment.amount for payment in cash_payments if
                                      payment.reconciled_invoice_ids and invoice.id in payment.reconciled_invoice_ids.ids)
                total_invoice_received += received_amount

                invoice_data.append({
                    'name': invoice.name,
                    'partner': invoice.partner_id.name,
                    'sales_man': invoice.invoice_user_id.name,
                    'payment_term': invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else invoice.invoice_date_due,
                    'invoice_date': invoice.invoice_date,
                    'amount': invoice.amount_total_signed,
                    'due_amount': invoice.amount_residual or 0.00,
                    'state': invoice.state,
                    'payment_state': invoice.payment_state,
                    'received': received_amount,
                })

            # Fetch bills
            bills = self.env['account.move'].search([
                ('invoice_date', '=', self.date),
                ('move_type', '=', 'in_invoice')
            ])
            total_bill_amount_total_signed = sum(bill.amount_total_signed for bill in bills)
            total_bill_due_amount = sum(bill.amount_residual for bill in bills)

            total_bill_paid_amount = 0
            bill_data = []
            for bill in bills:
                cash_payments = self.env['account.payment'].search([
                    ('date', '=', self.date),
                    ('partner_id', '=', bill.partner_id.id),
                    ('state', '=', 'posted'),
                    ('journal_id.type', '=', 'cash')
                ])
                paid_amount = sum(payment.amount for payment in cash_payments)
                total_bill_paid_amount += paid_amount
                print(bill.payment_state)
                bill_data.append({
                    'name': bill.name,
                    'partner': bill.partner_id.name,
                    'invoice_date': bill.invoice_date,
                    'amount': bill.amount_total_signed,
                    'amount_due': bill.amount_residual or 0.00,
                    'state': bill.state,
                    'payment_state': bill.payment_state,
                    'paid_amount': paid_amount,
                })

            # Get the list of move_ids from invoices and bills
            last_day = fields.Date.from_string(self.date) - timedelta(days=1)
            last_invoice_lines = self.env['account.move.line'].search([
                ('date', '<=', last_day),
                ('account_id', 'in', coas)
            ])

            # Received money and Paid bills (cash)
            received_payment = self.env['account.payment'].search(
                [('date', '=', self.date), ('journal_id.type', '=', 'cash')])

            total_received = 0
            receive_data = []

            total_bill = 0
            bill_payment_data = []
            for receive in received_payment:
                if receive.payment_type == 'inbound':
                    total_received += receive.amount
                    inv = self.env['account.move'].search([('name', '=', receive.ref)])
                    inv_date = inv.invoice_date
                    receive_data.append({
                        'name': receive.name,
                        'partner': receive.partner_id.name,
                        'invoice': receive.ref,
                        'amount': receive.amount,
                        'inv_date': inv_date,
                    })

                if receive.payment_type == 'outbound':
                    total_bill += receive.amount
                    bill = self.env['account.move'].search([('name', '=', receive.ref)])
                    bill_date = bill.invoice_date
                    bill_payment_data.append({
                        'name': receive.name,
                        'partner': receive.partner_id.name,
                        'invoice': receive.ref,
                        'amount': receive.amount,
                        'bill_date': bill_date,
                    })

            # Received money and Paid bills (bank)
            received_bank_payment = self.env['account.payment'].search(
                [('date', '=', self.date), ('journal_id.type', '=', 'bank')])

            total_bank_received = 0
            receive_bank_data = []

            total_bank_bill = 0
            bill_bank_payment_data = []
            for receive in received_bank_payment:
                if receive.payment_type == 'inbound':
                    total_bank_received += receive.amount
                    inv = self.env['account.move'].search([('name', '=', receive.ref)])
                    inv_date = inv.invoice_date
                    receive_bank_data.append({
                        'name': receive.name,
                        'partner': receive.partner_id.name,
                        'invoice': receive.ref,
                        'amount': receive.amount,
                        'inv_date': inv_date,
                    })

                if receive.payment_type == 'outbound':
                    total_bank_bill += receive.amount
                    bill = self.env['account.move'].search([('name', '=', receive.ref)])
                    bill_date = bill.invoice_date
                    bill_bank_payment_data.append({
                        'name': receive.name,
                        'partner': receive.partner_id.name,
                        'invoice': receive.ref,
                        'amount': receive.amount,
                        'bill_date': bill_date,
                    })

            data['form'].update({
                'received_bank': receive_bank_data,
                'total_bank_received': total_bank_received,
                'paid_bills_bank': bill_bank_payment_data,
                'total_bank_paid_bill': total_bank_bill,
            })

            # Transactions
            transaction_lines = self.env['account.move.line'].search([
                ('date', '=', self.date),
                ('account_id', 'in', coas),
                ('journal_id.type', '=', 'general'),
            ])
            total_credit = sum(credit.credit for credit in transaction_lines)
            total_debit = sum(debit.debit for debit in transaction_lines)

            transactions = []
            total_net = 0
            for transaction in transaction_lines:
                net_amount = transaction.debit - transaction.credit
                total_net += net_amount
                transactions.append({
                    'name': transaction.name,
                    'partner': transaction.partner_id.name,
                    'doc_num': transaction.move_id.name,
                    'doc_type': transaction.journal_id.name,
                    'ref': transaction.ref,
                    'debit': transaction.debit,
                    'credit': transaction.credit,
                    'net_amount': net_amount,
                })

            # CASH JOURNAL
            journal_ids = self.env['account.journal'].search([
                ('type', 'in', ['cash'])
            ])

            # Initialize a list to store payment data for each journal
            journal_data = []
            opening_total = 0
            cash_in_total = 0
            cash_out_total = 0

            for journal_id in journal_ids:
                # other transactions
                other_transaction_ids = self.env['account.move.line'].search([
                    ('date', '=', self.date),
                    ('account_id', '=', journal_id.default_account_id.id),
                    ('journal_id.type', '=', 'general'),
                ])

                # Get the list of move_ids from invoices and bills
                last_day = fields.Date.from_string(self.date) - timedelta(days=1)
                lst_payment_ids = self.env['account.move.line'].search([
                    ('account_id', '=', journal_id.default_account_id.id),
                    ('date', '<=', last_day),
                ])

                journal_open = sum([journal.balance for journal in lst_payment_ids])
                opening_total += journal_open

                receipt_voucher_ids = self.env['account.payment'].search([
                    ('journal_id', '=', journal_id.id),
                    ('date', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_type', '=', 'inbound')
                ])
                receipt_on_journal = sum([receipt.amount for receipt in receipt_voucher_ids]) + sum(
                    [other.debit for other in other_transaction_ids])
                cash_in_total += receipt_on_journal

                payment_voucher_ids = self.env['account.payment'].search([
                    ('journal_id', '=', journal_id.id),
                    ('date', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_type', '=', 'outbound')
                ])
                payment_on_journal = sum([payment.amount for payment in payment_voucher_ids]) + sum(
                    [other.credit for other in other_transaction_ids])
                cash_out_total += payment_on_journal

                journal_data.append({
                    'journal_id': journal_id.name,
                    'journal_open': journal_open,
                    'journal_receipt': receipt_on_journal,
                    'journal_paid': payment_on_journal,
                })

            lst_other_transaction_ids = self.env['account.move.line'].search([
                ('date', '<=', last_day),
                ('account_id', 'in', coas),
                ('journal_id.type', '=', 'general'),
            ])
            other_opening = sum([other.balance for other in lst_other_transaction_ids])
            # update totals
            opening_total += other_opening

            # Add the journal data list to the form
            data['form'].update({
                'journal_data': journal_data,
                'other_opening': other_opening,
                'opening_total': opening_total,
                'cash_in_total': cash_in_total,
                'cash_out_total': cash_out_total,
            })

            # BANK JOURNAL
            bank_journal_ids = self.env['account.journal'].search([
                ('type', 'in', ['bank'])
            ])

            bank_journal_data = []
            bank_opening_total = 0
            bank_in_total= 0
            bank_out_total = 0
            bank_other_opening = 0

            for journal_id in bank_journal_ids:
                """ No need OTHER TRANSACTION as this is already coming in cash. """

                last_day = fields.Date.from_string(self.date) - timedelta(days=1)
                lst_bank_payment_ids = self.env['account.move.line'].search([
                    ('account_id', '=', journal_id.default_account_id.id),
                    ('date', '<=', last_day),
                    ('move_id.state', '=', 'posted')
                ])
                bank_journal_open = sum([item.balance for item in lst_bank_payment_ids])
                bank_opening_total += bank_journal_open

                bank_receipt_voucher_ids = self.env['account.payment'].search([
                    ('journal_id', '=', journal_id.id),
                    ('date', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_type', '=', 'inbound')
                ])
                bank_receipt_on_journal = sum([item.amount for item in bank_receipt_voucher_ids])# + sum([item.debit for item in other_bank_transaction_ids])
                bank_in_total += bank_receipt_on_journal

                bank_payment_voucher_ids = self.env['account.payment'].search([
                    ('journal_id', '=', journal_id.id),
                    ('date', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_type', '=', 'outbound')
                ])
                payment_on_journal = sum([payment.amount for payment in bank_payment_voucher_ids]) # + sum([other.credit for other in other_bank_transaction_ids])
                bank_out_total += payment_on_journal

                bank_journal_data.append({
                    'journal_id': journal_id.name,
                    'journal_open': bank_journal_open,
                    'journal_receipt': bank_receipt_on_journal,
                    'journal_paid': payment_on_journal
                })

            data['form'].update({
                'bank_journal_data': bank_journal_data,
                'bank_other_opening': bank_other_opening,
                'bank_opening_total': bank_opening_total,
                'bank_in_total': bank_in_total,
                'bank_out_total': bank_out_total,
            })



            # pdc customer report
            pdc_report_ids = self.env['pdc.wizard'].search([
                ('company_id', '=', self.env.company.id),
                ('issue_date', '=', self.date),
                ('payment_type', '=', 'receive_money')
            ]).ids

            # pdc vendor report
            prd_vendor_report_ids = self.env['pdc.wizard'].search([
                ('company_id', '=', self.env.company.id),
                ('issue_date', '=', self.date),
                ('payment_type', '=', 'send_money')
            ]).ids
            # hr expenses
            hr_expense_ids = self.env['hr.expense'].search([
                ('company_id', '=', self.env.company.id),
                ('date', '=', self.date)
            ]).ids

            # Get all posted customer invoices for the date
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '=', self.date)
            ])

            # Nested dict: user -> payment_mode -> total amount
            user_payment_totals = defaultdict(lambda: defaultdict(float))
            all_payment_modes = set()

            for inv in invoices:
                user = inv.user_id.name if inv.user_id else "No User Assigned"
                payment_mode = inv.payment_mode.name if inv.payment_mode else "No Payment Mode"
                user_payment_totals[user][payment_mode] += inv.amount_total
                all_payment_modes.add(payment_mode)

            all_payment_modes = sorted(all_payment_modes)

            table_rows = []
            column_totals = {pm: 0.0 for pm in all_payment_modes}
            grand_total = 0.0

            for idx, (user_name, payment_dict) in enumerate(user_payment_totals.items(), start=1):
                row_total = sum(payment_dict.get(pm, 0.0) for pm in all_payment_modes)
                grand_total += row_total

                # Add to column totals
                for pm in all_payment_modes:
                    column_totals[pm] += payment_dict.get(pm, 0.0)

                row = {
                    'serial': idx,
                    'user_name': user_name,
                    'totals': [payment_dict.get(pm, 0.0) for pm in all_payment_modes],
                    'row_total': row_total
                }
                table_rows.append(row)

            grand_total_row = {
                'serial': '',
                'user_name': 'Total',
                'totals': [column_totals[pm] for pm in all_payment_modes],
                'row_total': grand_total
            }
            table_rows.append(grand_total_row)

            data['form'].update({
                'invoice_table_columns': ['Sr.', 'Sales Person'] + all_payment_modes + ['Total'],
                'invoice_table_rows': table_rows,
                'total_invoice_amount_total_signed': total_invoice_amount_total_signed,
                'total_invoice_due_amount': total_invoice_due_amount,
                'total_invoice_received': total_invoice_received,
                'invoices': invoice_data,
                'total_bill_amount_total_signed': total_bill_amount_total_signed,
                'total_bill_due_amount': total_bill_due_amount,
                'total_bill_paid_amount': total_bill_paid_amount,
                'bills': bill_data,
                'company': self.env.company.name,
                'report_title': f'Daily Transaction Report for {self.date}',
                'transactions': transactions,
                'total_credit': total_credit,
                'total_debit': total_debit,
                'total_net': total_net,
                'receipts': receive_data,
                'total_received': total_received,
                'paid_bills': bill_payment_data,
                'total_bill': total_bill,
                'pdc_report_ids': pdc_report_ids,
                'prd_vendor_report_ids': prd_vendor_report_ids,
                'hr_expense_ids': hr_expense_ids,
            })
        return self.env.ref('cpabooks_daily_reports.daily_transaction_report').report_action(self, data=data)


class DailyTransactionReportTemplate(models.AbstractModel):
    _name = 'report.cpabooks_daily_reports.daily_transaction_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        pdcs = self.env['pdc.wizard'].browse(data['form']['pdc_report_ids'])
        pdc_vendors = self.env['pdc.wizard'].browse(data['form']['prd_vendor_report_ids'])
        expenses = self.env['hr.expense'].browse(data['form']['hr_expense_ids'])
        data['form'].update({
            'pdcs': pdcs,
            'pdc_vendors': pdc_vendors,
            'expenses': expenses
        })
        print(data['form'])
        return data['form']
