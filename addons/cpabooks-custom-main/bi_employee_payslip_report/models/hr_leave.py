import calendar
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, Payslips, WorkedDays, InputLine
from odoo.addons.resource.models.resource import float_to_time
from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError
from odoo.tools.misc import get_lang
from babel.dates import format_datetime

class InheritHRLeave(models.Model):
    _inherit = 'hr.leave'

    # def create(self, vals_list):
    #     if self.holiday_status_i
    type_for = fields.Selection([
        ('regular', 'Regular Time Off'),
        ('public_holiday', 'Public Holiday'),
        ('leave_with_pay', 'Leave With Pay'),
        ('leave_with_out_pay', 'Leave With Out Pay'),
    ], required=True, string="Timeoff Type For",related="holiday_status_id.type_for",store=True)


    def action_draft(self):
        # if any(holiday.state not in ['confirm', 'refuse'] for holiday in self):
        #     raise UserError(_('Time off request state must be "Refused" or "To Approve" in order to be reset to draft.'))

        if self.holiday_type == 'employee' and self.state=='validate':
            get_contract = self.env['hr.contract'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
            if get_contract and get_contract.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                generated_dates=[]
                for day in range(self.request_date_from.day, self.request_date_to.day + 1):
                    generate_date = self.request_date_from + relativedelta(days=day) - relativedelta(days=self.request_date_from.day)
                    if generate_date not in generated_dates:
                        generated_dates.append(generate_date)
                for date in generated_dates:
                    day_of_week = (int(format_datetime(date-timedelta(days=2), 'e', locale=get_lang(self.env).code))) % 7
                    get_work_time=get_contract.structure_type_id.default_resource_calendar_id.attendance_ids.filtered(lambda x:x.dayofweek==str(day_of_week))
                    for line in get_work_time:
                        hour_from = float_to_time(line.hour_from)
                        hour_to = float_to_time(line.hour_to)
                        self.env['hr.work.entry'].sudo().create({
                            'name': 'Attendance: %s'% self.employee_id.name,
                            'employee_id':self.employee_id.id,
                            'work_entry_type_id': get_contract.structure_type_id.default_work_entry_type_id.id,
                            'date_start': datetime.combine(date, hour_from),
                            'date_stop': datetime.combine(date, hour_to)
                        })
        if self.holiday_type=='company' and self.state=='validate':
            get_contract = self.env['hr.contract'].sudo().search(
                [('company_id', '=', self.mode_company_id.id), ('state', '=', 'open'),('structure_type_id','in',self.env['hr.payroll.structure.type'].sudo().search([('default_struct_id.structure_type','=','basic_pay_office_stuff')]).ids)])
            if get_contract:
                for contract in get_contract:
                    generated_dates = []
                    for day in range(self.request_date_from.day, self.request_date_to.day + 1):
                        generate_date = self.request_date_from + relativedelta(days=day) - relativedelta(
                            days=self.request_date_from.day)
                        if generate_date not in generated_dates:
                            generated_dates.append(generate_date)
                    for date in generated_dates:
                        day_of_week = (int(format_datetime(date - timedelta(days=2), 'e',
                                                           locale=get_lang(self.env).code))) % 7
                        get_work_time = get_contract.structure_type_id.default_resource_calendar_id.attendance_ids.filtered(
                            lambda x: x.dayofweek == str(day_of_week))
                        for line in get_work_time:
                            hour_from = float_to_time(line.hour_from)
                            hour_to = float_to_time(line.hour_to)
                            self.env['hr.work.entry'].sudo().create({
                                'name': 'Attendance: %s' % contract.employee_id.name,
                                'employee_id': contract.employee_id.id,
                                'work_entry_type_id': contract.structure_type_id.default_work_entry_type_id.id,
                                'date_start': datetime.combine(date, hour_from),
                                'date_stop': datetime.combine(date, hour_to)
                            })

        self.write({
            'state': 'draft',
            'first_approver_id': False,
            'second_approver_id': False,
        })
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_draft()
            linked_requests.unlink()
        self.activity_update()
        return True

    def action_validate(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['confirm', 'validate1'] and holiday.validation_type != 'no_validation' for holiday
               in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})
        self.filtered(lambda holiday: holiday.validation_type == 'both').write(
            {'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write(
            {'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = None
                # employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                if holiday.holiday_status_id.type_for=='public_holiday':
                    employees=None
                else:
                    employees = None
                    # employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees=None
                # employees = holiday.department_id.member_ids
            if employees:
                conflicting_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True
                ).search([
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>', holiday.date_from),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_type', '=', 'employee'),
                    ('employee_id', 'in', employees.ids)])

                if conflicting_leaves:
                    # YTI: More complex use cases could be managed in master
                    if holiday.leave_type_request_unit != 'day' or any(
                            l.leave_type_request_unit == 'hour' for l in conflicting_leaves):
                        raise ValidationError(_('You can not have 2 time off that overlaps on the same day.'))

                # keep track of conflicting leaves states before refusal
                target_states = {l.id: l.state for l in conflicting_leaves}
                conflicting_leaves.action_refuse()
                split_leaves_vals = []
                for conflicting_leave in conflicting_leaves:
                    if conflicting_leave.leave_type_request_unit == 'half_day' and conflicting_leave.request_unit_half:
                        continue

                    # Leaves in days
                    if conflicting_leave.date_from < holiday.date_from:
                        before_leave_vals = conflicting_leave.copy_data({
                            'date_from': conflicting_leave.date_from.date(),
                            'date_to': holiday.date_from.date() + timedelta(days=-1),
                            'state': target_states[conflicting_leave.id],
                        })[0]
                        before_leave = self.env['hr.leave'].new(before_leave_vals)
                        before_leave._compute_date_from_to()

                        # Could happen for part-time contract, that time off is not necessary
                        # anymore.
                        # Imagine you work on monday-wednesday-friday only.
                        # You take a time off on friday.
                        # We create a company time off on friday.
                        # By looking at the last attendance before the company time off
                        # start date to compute the date_to, you would have a date_from > date_to.
                        # Just don't create the leave at that time. That's the reason why we use
                        # new instead of create. As the leave is not actually created yet, the sql
                        # constraint didn't check date_from < date_to yet.
                        if before_leave.date_from < before_leave.date_to:
                            split_leaves_vals.append(before_leave._convert_to_write(before_leave._cache))
                    if conflicting_leave.date_to > holiday.date_to:
                        after_leave_vals = conflicting_leave.copy_data({
                            'date_from': holiday.date_to.date() + timedelta(days=1),
                            'date_to': conflicting_leave.date_to.date(),
                            'state': target_states[conflicting_leave.id],
                        })[0]
                        after_leave = self.env['hr.leave'].new(after_leave_vals)
                        after_leave._compute_date_from_to()
                        # Could happen for part-time contract, that time off is not necessary
                        # anymore.
                        if after_leave.date_from < after_leave.date_to:
                            split_leaves_vals.append(after_leave._convert_to_write(after_leave._cache))

                split_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    leave_skip_state_check=True
                ).create(split_leaves_vals)

                split_leaves.filtered(lambda l: l.state in 'validate')._validate_leave_request()
            if employees:
                values = holiday._prepare_employees_holiday_values(employees)
                leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    leave_skip_state_check=True,
                ).create(values)

                leaves._validate_leave_request()

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        if self.holiday_type == 'employee':
            get_contract=self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','open')])
            if  get_contract and get_contract.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                work_days_time = self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.request_date_from),
                     ('date_start', '<=', self.request_date_to)])
                if work_days_time:
                    for data in work_days_time:
                        data.unlink()
        if self.holiday_type=='company':
            get_contract = self.env['hr.contract'].sudo().search(
                [('company_id', '=', self.mode_company_id.id), ('state', '=', 'open'),('structure_type_id','in',self.env['hr.payroll.structure.type'].sudo().search([('default_struct_id.structure_type','=','basic_pay_office_stuff')]).ids)])
            if get_contract:
                for contract in get_contract:
                    work_days_time = self.env['hr.work.entry'].sudo().search(
                        [('employee_id', '=', contract.employee_id.id), ('date_start', '>=', self.request_date_from),
                         ('date_start', '<=', self.request_date_to)])
                    if work_days_time:
                        for data in work_days_time:
                            data.unlink()

        return True

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                diff=holiday.date_to-holiday.date_from
                holiday.number_of_days = diff.days + 1
            else:
                holiday.number_of_days = 0

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.id
            if holiday.employee_id.user_id != self.env.user and self._origin.employee_id != holiday.employee_id:
                holiday.holiday_status_id = holiday.holiday_status_id