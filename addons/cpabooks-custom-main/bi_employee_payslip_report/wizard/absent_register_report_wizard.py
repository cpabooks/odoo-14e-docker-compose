import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT, BytesIO, xlsxwriter, base64
import pytz
from pytz import timezone

from dateutil.rrule import *
import calendar



class AbsentRegisterReportWizard(models.TransientModel):
    _name = 'absent.register.report.wizard'


    file = fields.Binary('File', readonly=True)
    file_name = fields.Char('Filename', readonly=True)
    from_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    to_date = fields.Date(string='To Date', required=True, default=fields.Date.today)
    employee_id=fields.Many2many('hr.employee',string="Employee")
    department_id=fields.Many2many('hr.department',string="Department")
    salary_structure=fields.Many2many('hr.payroll.structure.type',string="Salary Structure")
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company.id, store=True)

    # @api.onchange('department_id')
    # def set_employees_for_dept(self):
    #     get_employees=self.env['hr.employee'].sudo().search([('department_id','in',self.department_id.ids)])
    #     return {'domain': {'employee_id': [('id', 'in', get_employees.ids)]}}

    @api.onchange('salary_structure','department_id')
    def set_employees(self):
        employees = []
        if self.salary_structure:
            get_structure_type = self.env['hr.payroll.structure.type'].sudo().search(
                [('id', 'in', self.salary_structure.ids)])
            if get_structure_type:
                get_contracts = self.env['hr.contract'].sudo().search(
                    [('structure_type_id', 'in', get_structure_type.ids), ('active', '=', 'true'),
                     ('state', '=', 'open'), ('company_id', '=', self.env.company.id)])
                if get_contracts:
                    employees = get_contracts.employee_id.ids
                    if self.department_id:
                        emp_of_department=[emp.id for emp in get_contracts.employee_id if emp.department_id.id in self.department_id.ids]
                        employees=emp_of_department
                else:
                    employees = None
        else:
            get_employees = self.env['hr.employee'].sudo().search([('department_id', 'in', self.department_id.ids)])
            employees=get_employees.ids
        return {'domain': {'employee_id': [('id', 'in', employees)]}}

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'from_date': self.from_date, 'to_date': self.to_date, 'company_id': self.company_id.id,
                'employee_id': self.employee_id.ids,'department_id': self.department_id.ids,'salary_structure':self.salary_structure.ids
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('bi_employee_payslip_report.absent_register_report').report_action(
            self, data=data)

class ReportAbsentRegisterReportView(models.AbstractModel):
    """
        Abstract Model specially for report template.
        _name = Use prefix `report.` along with `module_name.report_name`
    """
    _name = 'report.bi_employee_payslip_report.absent_register_report_view'

    def _get_report_values(self, docids, data=None):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        company_id = data['form']['company_id']
        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']
        salary_structure_id=data['form']['salary_structure']

        get_lim_location_id = []
        start_date = datetime.strptime(from_date, DATE_FORMAT)
        end_date = datetime.strptime(to_date, DATE_FORMAT)
        date = (end_date + relativedelta(days=+ 1))


        employees=self.env['hr.employee']

        if salary_structure_id:
            get_structure_type = self.env['hr.payroll.structure.type'].sudo().search(
                [('id', 'in', salary_structure_id)])
            if get_structure_type:
                get_contracts = self.env['hr.contract'].sudo().search(
                    [('structure_type_id', 'in', get_structure_type.ids), ('active', '=', 'true'),
                     ('state', '=', 'open'), ('company_id', '=', int(company_id))])
                if get_contracts:
                    employees = get_contracts.employee_id
                    if department_id:
                        emp_of_department = [emp.id for emp in get_contracts.employee_id if
                                             emp.department_id.id in department_id]
                        employees = self.env['hr.employee'].sudo().search([('id','in',emp_of_department),('company_id','=',int(company_id))])

        if not salary_structure_id and department_id:
            employees = self.env['hr.employee'].sudo().search(
                [('department_id', 'in', department_id), ('company_id', '=', int(company_id))])

        # if department_id:
        #     if salary_structure_id:
        #         emp_of_department = [emp.id for emp in get_contracts.employee_id if
        #                              emp.department_id.id in self.department_id.ids]
        #         employees = self.env['hr.employee'].sudo().search(
        #             [('id', 'in', emp_of_department), ('company_id', '=', int(company_id))])
        #
        #     employees=self.env['hr.employee'].sudo().search([('department_id','in',department_id),('company_id','=',int(company_id))])

        if employee_id:
            employees=self.env['hr.employee'].sudo().search([('id','in',employee_id),('company_id','=',int(company_id))])

        if not department_id and not salary_structure_id:
            employees = self.env['hr.employee'].sudo().search([('company_id','=',int(company_id))])

        # if not department_id or employee_id:
        #     employees=self.env['hr.employee'].sudo().search([('id','in',employee_id),('company_id','=',int(company_id))])

        dates = [dt.date() for dt in rrule(DAILY, dtstart=start_date, until=end_date)]

        # for week in dates:
        #     print(week.weekday())
        weekend = self.env['week.day']
        emp_absent_register = []
        for emp in employees:
            employee=emp
            if employee.contract_id.weekend_day:
                weekend = employee.contract_id.weekend_day
            else:
                weekend = employee.contract_id.structure_type_id.default_struct_id.weekend_day

            # weekend = ['SATURDAY', 'SUNDAY']
            weekend_day = []
            for wd in weekend:
                if wd.name == 'SATURDAY':
                    weekend_day.append(calendar.SATURDAY)
                if wd.name == 'SUNDAY':
                    weekend_day.append(calendar.SUNDAY)
                if wd.name == 'MONDAY':
                    weekend_day.append(calendar.MONDAY)
                if wd.name == 'TUESDAY':
                    weekend_day.append(calendar.TUESDAY)
                if wd.name == 'WEDNESDAY':
                    weekend_day.append(calendar.WEDNESDAY)
                if wd.name == 'THURSDAY':
                    weekend_day.append(calendar.THURSDAY)
                if wd.name == 'FRIDAY':
                    weekend_day.append(calendar.FRIDAY)
            date_of_weekday = [day for day in dates if \
                                 day.weekday() in weekend_day]
            date_of_holiday=[]
            public_holidays = self.env['hr.leave'].sudo().search(
                [('mode_company_id', '=', employee.company_id.id),
                 ('date_from', '>=', from_date), ('date_to', '<=', to_date)], order='date_from')
            for date_length in public_holidays:
                if date_length.date_from.date()==date_length.date_to.date():
                    if date_length.date_from.date() not in date_of_holiday:
                        date_of_holiday.append(date_length.date_from.date())
                else:
                    # count=0
                    for date in range(date_length.date_from.date().day,date_length.date_to.date().day+1):
                        if date not in date_of_holiday:
                            date_of_holiday.append(date_length.date_from.date()+relativedelta(days=date)-relativedelta(days=date_length.date_from.date().day))
                        # count=count+1
            total_ignore_date=date_of_holiday+date_of_weekday
            date_of_workdays=[]
            for date in dates:
                if date not in total_ignore_date:
                    date_of_workdays.append(str(date))

            # for work_day in date_of_workdays:
            #     get_timesheet_line = self.env['account_analytic_line'].sudo().search([('date','in')])
            # get_timesheet_line=self.env['account.analytic.line']

            for date in date_of_workdays:
                get_timesheet_line = self.env['account.analytic.line'].sudo().search([('date', '=',date),('company_id','=',employee.company_id.id),('employee_id','=',employee.id)])
                if get_timesheet_line:
                    for line in get_timesheet_line:
                        if line.unit_amount==0:
                            vals={
                                'code':employee.barcode,
                                'name':employee.name,
                                'date_absent':date,
                                'remarks':line.name
                            }
                            emp_absent_register.append(vals)
                else:
                    vals = {
                        'code': employee.barcode,
                        'name': employee.name,
                        'date_absent': date,
                        'remarks': ''
                    }
                    emp_absent_register.append(vals)
        report_name = 'bi_employee_payslip_report.absent_register_report_view'
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        docs=self.env[report.model].browse(data['ids'])
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'from_date': from_date,
            'to_date': to_date,
            'absent_register': emp_absent_register,
        }


