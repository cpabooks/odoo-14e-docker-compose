from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class DailySalesAnalysis(models.TransientModel):
    _name = 'daily.sales.analysis'
    _description = 'Daily Sales Analysis Report'

    start_date = fields.Date('From', default=lambda self: date.today().replace(day=1))
    end_date = fields.Date('To', default=date.today())

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_('Start Date must be smaller than End date'))
            if not rec.start_date or not rec.end_date:
                raise ValidationError(_('Both Start Date and End Date are required'))

    def check_report(self):
        data = {'form': self.read()[0]}
        dates = []
        daily_totals = []

        # Calculate previous month date range
        previous_month_start_date = self.start_date - relativedelta(months=1)
        previous_month_end_date = self.end_date - relativedelta(months=1)

        # Initialize cumulative variables
        cm_cumulative = pm_cumulative = 0

        # Loop through each day in the range
        current_date = self.start_date
        while current_date <= self.end_date:
            # CM: Invoices of the current month
            cm_invoices = self.env['account.move'].search([
                ('state', 'not in', ['draft', 'cancel']),
                ('invoice_date', '=', current_date),
                ('move_type', '=', 'out_invoice'),
            ])
            cm_total = sum(cm_invoices.mapped('amount_total'))

            # PM: Invoices of the previous month for the same date
            pm_date = previous_month_start_date + (current_date - self.start_date)
            pm_invoices = self.env['account.move'].search([
                ('state', 'not in', ['draft', 'cancel']),
                ('invoice_date', '=', pm_date),
                ('move_type', '=', 'out_invoice'),
            ])
            pm_total = sum(pm_invoices.mapped('amount_total'))

            # Calculate cumulative totals
            cm_cumulative += cm_total
            pm_cumulative += pm_total

            # Calculate averages
            days_passed = (current_date - self.start_date).days + 1
            cm_average = cm_cumulative / days_passed
            pm_average = pm_cumulative / days_passed

            # Calculate variance
            variance = cm_average - pm_average

            daily_totals.append({
                'date': current_date.strftime('%d'),
                'cm_total': cm_total,
                'cm_cumulative': cm_cumulative,
                'cm_average': cm_average,
                'pm_total': pm_total,
                'pm_cumulative': pm_cumulative,
                'pm_average': pm_average,
                'variance': variance,
            })
            current_date += relativedelta(days=1)

        data['daily_totals'] = daily_totals
        return self.env.ref('cpabooks_daily_reports.daily_sales_analysis_report').report_action(self, data=data)
