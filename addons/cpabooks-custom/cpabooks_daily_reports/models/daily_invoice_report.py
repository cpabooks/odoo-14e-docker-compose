from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import datetime

class DailyInvoiceReport(models.TransientModel):
    _name = 'daily.invoice.report'
    _description = 'Daily Invoice Report'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date', default=date.today())
    invoice_bill_options = fields.Selection([
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('last_month', 'Last Month'),
    ], 'Generate Report For')

    def check_report(self):
        today = datetime.date.today()
        report_title = ""

        if self.invoice_bill_options == 'today':
            self.start_date = today
            self.end_date = today
            report_title = _("Today - %s") % today.strftime('%Y-%m-%d')
        elif self.invoice_bill_options == 'week':
            self.start_date = today - timedelta(days=today.weekday())
            self.end_date = today
            report_title = _("This Week (%s - %s)") % (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))
        elif self.invoice_bill_options == 'month':
            self.start_date = today.replace(day=1)
            self.end_date = today
            report_title = _("This Month (%s - %s)") % (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))
        elif self.invoice_bill_options == 'last_month':
            first_day_of_current_month = today.replace(day=1)
            self.start_date = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
            self.end_date = first_day_of_current_month - timedelta(days=1)
            report_title = _("Last Month (%s - %s)") % (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))
        else:
            report_title = _("From %s to %s") % (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))

        if not self.start_date or not self.end_date:
            raise ValidationError(_("Please input 'Start Date' and 'End Date'"))

        if self.start_date > self.end_date:
            raise ValidationError(_("'Start Date' must be earlier than 'End Date'"))

        invoices = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('move_type', '=', 'out_invoice')  # Customer invoices
        ])

        cash_receipts = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['in_payment', 'partial'])
        ])

        bills = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('move_type', '=', 'in_invoice')  # Vendor bills
        ])

        cash_payments = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('move_type', '=', 'in_invoice'),
            ('payment_state', 'in', ['in_payment', 'partial'])
        ])

        daily_totals = {}
        for invoice in invoices:
            invoice_date = invoice.invoice_date
            if invoice_date not in daily_totals:
                daily_totals[invoice_date] = {
                    'invoices': 0, 'cash_receipts': 0, 'bills': '-', 'cash_payments': 0,
                    'sale_diff': 0, 'payment_diff': 0
                }
            daily_totals[invoice_date]['invoices'] += invoice.amount_total

        for receipt in cash_receipts:
            receipt_date = receipt.invoice_date
            if receipt_date not in daily_totals:
                daily_totals[receipt_date] = {
                    'invoices': 0, 'cash_receipts': 0, 'bills': '-', 'cash_payments': 0,
                    'sale_diff': 0, 'payment_diff': 0
                }
            daily_totals[receipt_date]['cash_receipts'] += receipt.amount_total

        for bill in bills:
            bill_date = bill.invoice_date
            if bill_date not in daily_totals:
                daily_totals[bill_date] = {
                    'invoices': '-', 'cash_receipts': '-', 'bills': 0, 'cash_payments': '-',
                    'sale_diff': 0, 'payment_diff': 0
                }
            if daily_totals[bill_date]['bills'] == '-':
                daily_totals[bill_date]['bills'] = 0
            daily_totals[bill_date]['bills'] += bill.amount_total

        for payment in cash_payments:
            payment_date = payment.invoice_date
            if payment_date not in daily_totals:
                daily_totals[payment_date] = {
                    'invoices': '-', 'cash_receipts': '-', 'bills': '-', 'cash_payments': 0,
                    'sale_diff': 0, 'payment_diff': 0
                }
            if daily_totals[payment_date]['cash_payments'] == '-':
                daily_totals[payment_date]['cash_payments'] = 0
            daily_totals[payment_date]['cash_payments'] += payment.amount_total

        # Calculate sale_diff and payment_diff
        for date, totals in daily_totals.items():
            invoices = totals['invoices'] if totals['invoices'] != '-' else 0
            bills = totals['bills'] if totals['bills'] != '-' else 0
            cash_receipts = totals['cash_receipts'] if totals['cash_receipts'] != '-' else 0
            cash_payments = totals['cash_payments'] if totals['cash_payments'] != '-' else 0
            daily_totals[date]['sale_diff'] = invoices - bills
            daily_totals[date]['payment_diff'] = cash_receipts - cash_payments

        # Convert daily_totals to a list of dictionaries to ensure it's serializable
        data = {
            'form': self.read()[0],
            'report_title': report_title,
            'daily_totals': [{
                'date': date,
                'invoices': totals['invoices'],
                'cash_receipts': totals['cash_receipts'],
                'bills': totals['bills'],
                'cash_payments': totals['cash_payments'],
                'sale_diff': totals['sale_diff'],
                'payment_diff': totals['payment_diff']
            } for date, totals in daily_totals.items()]
        }

        return self.env.ref('cpabooks_daily_reports.daily_invoice_report').report_action(self, data=data)




class DailyInvoiceReportTemplate(models.AbstractModel):
    _name = 'report.cpabooks_daily_reports.daily_invoice_report_template'
    _description = 'Daily Invoice Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = data['form']
        daily_totals = data['daily_totals']
        print(self.env.company)
        return {
            'doc_ids': docids,
            'doc_model': 'daily.invoice.report',
            'docs': docs,
            'daily_totals': daily_totals,
            'company_id': self.env.company,
        }
