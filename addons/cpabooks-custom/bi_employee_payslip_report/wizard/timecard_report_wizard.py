import base64
import calendar
from datetime import datetime,timedelta,date
from io import BytesIO

from odoo import models, fields

class timeCardWizard(models.TransientModel):
    _name = 'timecard.wizard'
    _description = 'Employee Timecard Wizard'

    emp_id = fields.Many2one('hr.employee', string='Employee',required=1)

    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Month', required=True,default=lambda self: self._get_previous_month())

    def _get_previous_month(self):
        today = datetime.now()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month
        return last_day_of_previous_month.strftime('%m')

    year = fields.Selection(
        [(str(year), str(year)) for year in range(2000, 2101)],
        string='Year',
        required=True,default=lambda self: str(datetime.now().year)
    )
    company_id=fields.Many2one('res.company',string="Company", default=lambda self:self.env.company.id)

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'company_id': self.company_id.id,
                'employee_id': self.emp_id.id,
                'month': self.month,
                'year':self.year,
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('bi_employee_payslip_report.timecard_report').report_action(
            self, data=data)


class ReportTimeCardReportView(models.AbstractModel):
    _name = 'report.bi_employee_payslip_report.timecard_report_view'

    def _get_report_values(self, docids, data=None):
         month = data['form']['month']
         year = data['form']['year']
         employee_id=data['form']['employee_id']
         employee=self.env['hr.employee'].sudo().search([('id','=',int(employee_id))])
         month_name = datetime.strptime(str(month), '%m').strftime('%b')
         year_name=int(year)
         _, last_day = calendar.monthrange(year_name, int(month))

         report_name = 'bi_employee_payslip_report.timecard_report_view'
         report = self.env['ir.actions.report']._get_report_from_name(report_name)
         docs = self.env[report.model].browse(data['ids'])

         # Get regular work hours from salary structure
         regular_hours = employee.contract_id.sudo().structure_type_id.default_struct_id.standard_working_hour or 8.0  # Default to 8 if not set
         weekend_days=employee.contract_id.sudo().structure_type_id.default_struct_id.weekend_day
         weekday_names=[wd.name.upper() for wd in weekend_days]

         # Prepare daily timesheet data
         timesheet_data = []
         total_regular = 0
         total_overtime = 0
         total_hours = 0

         payslip = self.env['hr.payslip'].search([
             ('employee_id', '=', int(employee_id)),
             ('date_to', '>=', f"{year}-{month}-01"),
             ('date_to', '<=', f"{year}-{month}-{last_day}")
         ], limit=1)

         for day in range(1, last_day + 1):
             current_date  = date(year_name, int(month), day)
             date_str = current_date .strftime('%d-%b-%Y')

             # Get timesheet entries for this date
             domain = [
                 ('employee_id', '=', employee.id),
                 ('date', '=', current_date),
             ]
             if weekday_names and current_date.strftime('%A').upper() in weekday_names:
                 timesheet_data.append({
                     'date': date_str,
                     'day_name': current_date.strftime('%a'),
                     'is_weekend': True,  # Flag to identify weekends in template
                     'regular_hours': '',
                     'overtime_hours': '',
                     'total_hours': ''
                 })
             else:
                 lines = self.env['account.analytic.line'].search(domain)
                 day_hours = sum(line.unit_amount for line in lines)

                 # Calculate regular vs overtime
                 # regular = min(day_hours, regular_hours)
                 regular = regular_hours
                 overtime = max(0, day_hours - regular_hours)

                 timesheet_data.append({
                     'date': date_str,
                     'day_name': current_date.strftime('%a'),
                     'is_weekend': False,
                     'regular_hours': regular,
                     'overtime_hours': overtime,
                     'total_hours': day_hours,
                 })

                 total_regular += regular
                 total_overtime += overtime
                 total_hours += day_hours
         return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'report_title': f"Timecard for the month of {month_name}, {year_name}",
             'salary_title': f"Salary Calculation {month_name}, {year_name}",
             'employee': {
                 'name': employee.name,
                 'code': 'N/A',
                 'trade': employee.job_id.name if employee.job_id else 'N/A',
                 'month_range': f"FROM 01.{int(month):02d}.{year_name % 100} TO {last_day}.{int(month):02d}.{year_name % 100}"
             },
             'company_details': {
                 'name': self.env.company.name,
                 'site': 'N/A',
                 'location': f"{self.env.company.city or ''}, {self.env.company.country_id.name or ''}".strip(', ')
             },
             'timesheet_data': timesheet_data,
             'totals': {
                 'regular': total_regular,
                 'overtime': total_overtime,
                 'total': total_hours,
             },
             'payslip': payslip,
             'regular_hours_per_day': regular_hours,
        }