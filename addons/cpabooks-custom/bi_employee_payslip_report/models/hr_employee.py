import calendar
import datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_timesheet_cost(self):
        for rec in self:
            try:
                rec.timesheet_cost = rec.contract_id.salary_per_h if rec.contract_id and rec.contract_id.state == 'open' else 0.0
                _logger.success(rec.timesheet_cost)
            except Exception as e:
                _logger.error(e)

    agent_routing_code=fields.Many2one('agent.routing',string="Agent Routing")
    emp_mol_id=fields.Char(string="Employee MOL ID")
    accommodation = fields.Selection([('accom1', 'Accom 1'),('accom2','Accom 2')], 'Accommodation', default='accom1')
    eid_no = fields.Char('EID No', groups="hr.group_hr_user", tracking=True)
    work_permit_expire = fields.Date('Work Permit Expire Date', groups="hr.group_hr_user", tracking=True)
    timesheet_cost = fields.Monetary('Timesheet Cost', currency_field='currency_id',
    	groups="hr.group_hr_user", default=0.0 , compute=_compute_timesheet_cost, readonly=False, store=True)
    # structure_type_id = fields.Many2one('hr.payroll.structure.type', related='contract_id.structure_type_id',
    #                                     string="Salary Structure Type",
    #                                     readonly=True, store=True)

    # def create_contract(self):
    #     for rec in self:
    #         check_existing_active_contact=self.env['hr.contract'].sudo().search([('employee_id','=',rec.id),
    #                                                                                   ('active','=',True),('state','=','open')])
    #         check_existing_contact = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.id),('active','=',True)])
    #         if check_existing_active_contact:
    #             raise ValidationError(_("An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts)"))
    #         else:
    #             if check_existing_contact:
    #                 get_number=len(check_existing_contact)
    #             else:
    #                 get_number=0
    #             get_struct_type=self.env['hr.payroll.structure.type'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1)
    #             if get_struct_type:
    #                 get_struct_type.default_struct_id=self.env['hr.payroll.structure'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1).id
    #             vals={
    #                 'name':rec.name+' Cont.'+str(get_number).zfill(2) if get_number<10 else str(get_number),
    #                 'structure_type_id': self.env['hr.payroll.structure.type'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1).id,
    #                 'wage':0,
    #                 'state':'open',
    #                 'employee_id':rec.id,
    #                 'active':True,
    #                 'resource_calendar_id':  rec.resource_calendar_id.id
    #             }
    #             self.env['hr.contract'].sudo().create(vals)
    #     return True


    # def get_not_overtime(self, id, start_date, end_date):
    #     not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
    #     return not_hour
    #
    # def get_hot_overtime(self, id, start_date, end_date):
    #     not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
    #     return hot_hour
    #
    # def employee_monthly_work_history(self, id, start_date, end_date):
    #     standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
    #     c = calendar.Calendar()
    #
    #     year = start_date.year
    #     month = start_date.month
    #     calendar_day = calendar.monthrange(year, month)
    #     calendar_days = calendar_day[1]
    #
    #     weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
    #     monthcal = c.monthdatescalendar(year, month)
    #     weekend_day = []
    #     weekend_day.append(calendar.SUNDAY)
    #     for wd in weekend:
    #         if wd.name == 'SATURDAY':
    #             weekend_day.append(calendar.SATURDAY)
    #         if wd.name == 'SUNDAY':
    #             weekend_day.append(calendar.SUNDAY)
    #         if wd.name == 'MONDAY':
    #             weekend_day.append(calendar.MONDAY)
    #         if wd.name == 'TUESDAY':
    #             weekend_day.append(calendar.TUESDAY)
    #         if wd.name == 'WEDNESDAY':
    #             weekend_day.append(calendar.WEDNESDAY)
    #         if wd.name == 'THURSDAY':
    #             weekend_day.append(calendar.THURSDAY)
    #         if wd.name == 'FRIDAY':
    #             weekend_day.append(calendar.FRIDAY)
    #     # no_of_weekend=0
    #     # for week in monthcal:
    #     #     for day in week:
    #     #         if
    #     number_of_weekday = len([day for week in monthcal for day in week if \
    #                              day.weekday() in weekend_day and \
    #                              day.month == month])
    #
    #     monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
    #         [('employee_id', '=', id), ('date', '>=', start_date),
    #          ('date', '<=', end_date)]).mapped('unit_amount'))
    #
    #     #######PUBLIC HOLIDAY###########
    #     ph_day = 0
    #     public_holidays = self.env['hr.leave'].sudo().search(
    #         [('mode_company_id', '=', self.company_id.id),
    #          ('date_from', '>=', start_date), ('date_to', '<=', end_date)], order='date_from')
    #
    #     # public_holiday_work_hour = 0
    #
    #     # CALCULATION OF WEEKEND WORK HOUR
    #     num_days = calendar.monthrange(year, month)[1]
    #     dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
    #     weekend_date_this_month = []
    #     for date in dates:
    #         day_num = date.weekday()
    #         # day = calendar.day_name[day_num]
    #         if day_num in weekend_day:
    #             weekend_date_this_month.append(date)
    #     public_holiday_work_hour = 0
    #     if weekend_date_this_month:
    #         for date in weekend_date_this_month:
    #             min_time = datetime.datetime.min.time()
    #             max_time = datetime.datetime.max.time()
    #             my_min_datetime = datetime.datetime.combine(date, min_time)
    #             my_max_datetime = datetime.datetime.combine(date, max_time)
    #
    #             public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
    #                 [('employee_id', '=', self.employee_id.id), ('date', '>=', my_min_datetime),
    #                  ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
    #     # CALCULATION OF WEEKEND WORK HOUR
    #     for holiday in public_holidays:
    #         public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
    #             [('employee_id', '=', id), ('date', '>=', holiday.date_from),
    #              ('date', '<=', holiday.date_to)]).mapped('unit_amount'))
    #         ph_day += holiday.number_of_days
    #     #######PUBLIC HOLIDAY###########
    #
    #     net_working_day = calendar_days - number_of_weekday
    #     net_working_hour = round(calendar_days * standard_work_hour - number_of_weekday * standard_work_hour, 2)
    #     HOT_day = ph_day
    #     # HOT_Hour = round(ph_day * standard_work_hour, 2)
    #     HOT_Hour = round(public_holiday_work_hour, 2)
    #     monthly_total_day = monthly_total_work_hour / standard_work_hour
    #     monthly_total_hour = round(monthly_total_work_hour, 2)
    #     net_worked_day = monthly_total_day - HOT_day
    #     net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)
    #
    #     not_day = net_working_day - net_worked_day
    #     not_hour = net_worked_hour - net_working_hour
    #
    #     return not_hour, HOT_Hour

    # @api.model
    # def create(self, vals):
    #     employee = super(HrEmployee, self).create(vals)
    #
    #     self.env['ctc.report.formula.line'].create({
    #         'employee_id': employee.id,
    #     })
    #
    #     return employee
    #
    # def unlink(self):
    #     ctc_lines = self.env['ctc.report.formula.line'].sudo().search([('employee_id', 'in', self.ids)])
    #     if ctc_lines:
    #         ctc_lines.unlink()
    #     return super(HrEmployee, self).unlink()

    def get_not_overtime(self, id, start_date, end_date):
        if self.contract_id.structure_type_id.default_struct_id.overtime_cal_method=='on_monthly':
            not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        else:
            absent_hour, not_hour, hot_hour = self.employee_monthly_work_history(id, start_date, end_date)
        return not_hour

    def get_hot_overtime(self, id, start_date, end_date):
        if self.contract_id.structure_type_id.default_struct_id.overtime_cal_method == 'on_monthly':
            not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        else:
            absent_hour, not_hour, hot_hour = self.employee_monthly_work_history(id, start_date, end_date)
        return hot_hour

    def get_absent_time(self, id, start_date, end_date):
        absent_hour, not_hour, hot_hour = self.employee_monthly_work_history(id, start_date, end_date)
        return absent_hour

    def get_leave_with_pay(self, id, start_date, end_date):
        user_timezone = int(fields.datetime.now(pytz.timezone(self.env.user.tz or 'GMT')).strftime("%Z"))
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        leave_with_pay_dates = []
        month = start_date.month
        year = end_date.year
        # query = """select date_from,date_to  from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}' and employee_id={} and state='{}'""".format(
        #     start_date, month, end_date, year, 'leave_with_pay',id,'validate')
        query = """select date_from,date_to  from hr_leave  where ((date_from::DATE between '{}'::DATE and '{}'::DATE) or (date_to::DATE between '{}'::DATE and '{}'::date)) 
                and type_for='{}' and employee_id={} and state='{}'""".format(
            start_date-datetime.timedelta(days=1), end_date-datetime.timedelta(days=1),start_date-datetime.timedelta(days=1),
            end_date-datetime.timedelta(days=1), 'leave_with_pay', id, 'validate')
        self._cr.execute(query)

        get_leave_with_pay_result = self._cr.fetchall()


        for result in get_leave_with_pay_result:
            result_list = list(result)
            result_list[0] = result_list[0] + datetime.timedelta(hours=user_timezone)
            date_from = result_list[0].date()
            result_list[1] = result_list[1] + datetime.timedelta(hours=user_timezone)
            date_to = result_list[1].date()


            # date_from = result[11].date()+datetime.timedelta(days=1)
            # date_to = result[12].date()+datetime.timedelta(days=1)
            # date_to = end_date
            if date_from < end_date and date_to<start_date:
                date_to = end_date
            if date_from<start_date:
                date_from=start_date
            if date_from == date_to:
                if date_from not in leave_with_pay_dates:
                    leave_with_pay_dates.append(date_from)
            else:
                # count=0
                if date_from.day>date_to.day:
                    date_from=start_date

                for day in range(date_from.day, date_to.day+1):
                    # generate_date = start_date + relativedelta(days=day.day) - relativedelta(days=start_date.day)
                    generate_date = start_date+ relativedelta(days=day) - relativedelta(days=start_date.day)
                    if generate_date not in leave_with_pay_dates:
                        leave_with_pay_dates.append(generate_date)

        leave_with_pay = float(len(leave_with_pay_dates))
        leave_with_pay_hour=leave_with_pay*standard_work_hour
        return leave_with_pay_hour

    def get_leave_with_pay_dates(self, id, start_date, end_date):
        user_timezone = int(fields.datetime.now(pytz.timezone(self.env.user.tz or 'GMT')).strftime("%Z"))
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        leave_with_pay_dates = []
        month = start_date.month
        year = end_date.year
        # query = """select date_from,date_to  from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}' and employee_id={} and state='{}'""".format(
        #     start_date, month, end_date, year, 'leave_with_pay',id,'validate')
        query = """select date_from,date_to  from hr_leave  where ((date_from::DATE between '{}'::DATE and '{}'::DATE) or (date_to::DATE between '{}'::DATE and '{}'::date)) 
                and type_for='{}' and employee_id={} and state='{}'""".format(
            start_date-datetime.timedelta(days=1), end_date-datetime.timedelta(days=1),start_date-datetime.timedelta(days=1),
            end_date-datetime.timedelta(days=1), 'leave_with_pay', id, 'validate')
        self._cr.execute(query)

        get_leave_with_pay_result = self._cr.fetchall()


        for result in get_leave_with_pay_result:
            result_list = list(result)
            result_list[0] = result_list[0] + datetime.timedelta(hours=user_timezone)
            date_from = result_list[0].date()
            result_list[1] = result_list[1] + datetime.timedelta(hours=user_timezone)
            date_to = result_list[1].date()


            # date_from = result[11].date()+datetime.timedelta(days=1)
            # date_to = result[12].date()+datetime.timedelta(days=1)
            # date_to = end_date
            if date_from < end_date and date_to<start_date:
                date_to = end_date
            if date_from<start_date:
                date_from=start_date
            if date_from == date_to:
                if date_from not in leave_with_pay_dates:
                    leave_with_pay_dates.append(date_from)
            else:
                # count=0
                if date_from.day>date_to.day:
                    date_from=start_date

                for day in range(date_from.day, date_to.day+1):
                    # generate_date = start_date + relativedelta(days=day.day) - relativedelta(days=start_date.day)
                    generate_date = start_date+ relativedelta(days=day) - relativedelta(days=start_date.day)
                    if generate_date not in leave_with_pay_dates:
                        leave_with_pay_dates.append(generate_date)

        leave_with_pay = float(len(leave_with_pay_dates))
        leave_with_pay_hour=leave_with_pay*standard_work_hour
        return leave_with_pay_dates

    def get_leave_with_out_pay(self, id, start_date, end_date):
        user_timezone=int(fields.datetime.now(pytz.timezone(self.env.user.tz or 'GMT')).strftime("%Z"))
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        leave_with_out_pay_dates = []
        month = start_date.month
        year = end_date.year
        query = """select date_from,date_to  from hr_leave  where  ((date_from::DATE between '{}'::DATE and '{}'::DATE) or (date_to::DATE between '{}'::DATE and '{}'::date)) 
         and type_for='{}' and employee_id={} and state='{}'""".format(
            start_date, end_date,start_date, end_date, 'leave_with_out_pay',id,'validate')
        self._cr.execute(query)

        get_leave_with_out_pay_result = self._cr.fetchall()

        # get_leave_with_out_pay_result_new=self.env['hr.leave'].sudo().search([('employee_id','=',id),('type_for','=','leave_with_out_pay'),('state','=','validate'),
        #                                                                   (('date_from','>=',str(start_date)),('date_from','<=',str(end_date)),'|',('date_to','>=',str(start_date)),
        #                                                                    ('date_from','<=',str(end_date)))])
        for result in get_leave_with_out_pay_result:
            # date_from = result[12].date()
            # date_to = end_date
            # if result[13].date() < end_date:
            #     date_to = result[13].date()
            # if date_from == date_to:
            #     if date_from not in leave_with_out_pay_dates:
            #         leave_with_out_pay_dates.append(date_from)
            result_list=list(result)
            result_list[0]=result_list[0]+datetime.timedelta(hours=user_timezone)
            date_from = result_list[0].date()
            result_list[1] = result_list[1] + datetime.timedelta(hours=user_timezone)
            date_to = result_list[1].date()
            # date_to = end_date
            if result_list[1].date() < end_date and result_list[0].date() < start_date:
                date_to = end_date
            if result_list[0].date() < start_date:
                date_from = start_date
            if result_list[1].date() > end_date:
                date_to=end_date
            # if date_from.month == start_date.month:
            #     if date_from.day > start_date.day:
            #         date_from = date_from
            #         date_to = end_date
            #     elif date_from.day == start_date.day:
            #         date_from = start_date
            #         date_to = end_date
            # if date_to.month == start_date.month:
            #     date_from = start_date
            #     date_to = end_date
            if date_from == date_to:
                if date_from not in leave_with_out_pay_dates:
                    leave_with_out_pay_dates.append(date_from)
            else:
                # count=0
                if date_from.month==start_date.month:
                    if date_from.day>start_date.day:
                        date_from=date_from
                        date_to=date_to
                    elif date_from.day==start_date.day:
                        date_from=start_date
                        date_to=date_to
                elif date_to.month==start_date.month:
                    date_from=start_date
                    date_to=end_date

                # elif date_from.day>date_to.day:
                #     date_from=start_date
                for day in range(date_from.day, date_to.day + 1):
                    # generate_date = start_date + relativedelta(days=day) - relativedelta(days=start_date.day)
                    generate_date = start_date+ relativedelta(days=day)- relativedelta(days=start_date.day)
                    if generate_date not in leave_with_out_pay_dates:
                        leave_with_out_pay_dates.append(generate_date)
        ##********************get works dates********************##
        worked_dates=[]
        if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
            work_days_time = self.env['hr.work.entry'].sudo().search(
                [('employee_id', '=', id), ('date_start', '>=', start_date),
                 ('date_start', '<=', end_date)])

            # for line in monthly_total_work_details:
            #     worked_dates.append(line.date_start)


        else:
            work_days_time = self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', start_date),
                 ('date', '<=', end_date)])

        monthly_total_work_hour = 0
        monthly_not_hour = 0
        work_date_dict = dict()
        for time in work_days_time:
            if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                if time.date_start.date() not in work_date_dict.keys():
                    work_date_dict[time.date_start.date()] = time.duration
                else:
                    work_date_dict[time.date_start.date()] += time.duration
            else:
                if time.date not in work_date_dict.keys():
                    work_date_dict[time.date] = time.unit_amount
                else:
                    work_date_dict[time.date] += time.unit_amount

        for time in work_date_dict.keys():
            if work_date_dict[time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                monthly_total_work_hour += work_date_dict[time]
            else:
                monthly_not_hour += work_date_dict[
                                        time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

            # for line in monthly_total_work_details:
            #     worked_dates.append(line.date)



        ##********************get works dates********************##
        #if leave without pay fall in already worked day**********************
        leave_with_out_pay=0.0
        leave_without_pay_valid_dates=[]
        for leave in leave_with_out_pay_dates:
            if leave not in work_date_dict.keys() or (leave  in work_date_dict.keys() and work_date_dict[leave]==0):
                leave_with_out_pay+=1
                leave_without_pay_valid_dates.append(leave)

        # copy_leave_without_pay_valid_dates=leave_without_pay_valid_dates

        # if leave without pay fall in already worked day**********************
        #if leave without pay fall in weekend**********************************
        c = calendar.Calendar()

        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        weekend = self.env['week.day']
        if self.contract_id.weekend_day:
            weekend = self.contract_id.weekend_day
        else:
            weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
        monthcal = c.monthdatescalendar(year, month)
        weekend_day = []
        # weekend_day.append(calendar.SUNDAY)
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
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        weekend_date_this_month = []
        for date in dates:
            day_num = date.weekday()
            # day = calendar.day_name[day_num]
            if day_num in weekend_day:
                weekend_date_this_month.append(date)

        weekend_need_to_remove=[]
        # if len(weekend_date_this_month)>0:
        #     for leave in leave_without_pay_valid_dates:
        #         if leave in weekend_date_this_month:
        #             weekend_need_to_remove.append(leave)

        # for date in weekend_date_this_month:
        #     if date in leave_without_pay_valid_dates:
        #         leave_without_pay_valid_dates.remove(date)





        # if leave without pay fall in weekend****************************************
        # if leave without pay fall in public holiday**********************************
        public_holidays = self.env['hr.leave'].sudo().search(
            [('mode_company_id', '=', self.contract_id.employee_id.company_id.id),
             ('date_from', '>=', start_date), ('date_to', '<=', end_date)], order='date_from')

        public_holiday_dates = []

        for holiday in public_holidays:
            # need to remove weekend date from here
            from_date = holiday.date_from
            to_date = holiday.date_to.date()
            delta = to_date - from_date.date()
            for i in range(delta.days + 1):
                day = from_date + datetime.timedelta(days=i)
                public_holiday_dates.append(day.date())
        # if leave without pay fall in public holiday**********************************

        # need_to_remove_dates=[]
        # if len(public_holiday_dates)>0:
        #     for leave in leave_without_pay_valid_dates:
        #         if leave in public_holiday_dates:
        #             need_to_remove_dates.append(leave)

        for date in public_holiday_dates:
            if date in leave_without_pay_valid_dates:
                leave_without_pay_valid_dates.remove(date)
        count = 0
        leave_without_pay_valid_dates_extra = []
        for weekend in weekend_date_this_month:
            for leave in leave_without_pay_valid_dates:
                if abs(weekend.day - leave.day) == 1:
                    # leave_without_pay_valid_dates_extra.append(weekend)
                    # break
                    count += 1
                    if count == 2:
                        leave_without_pay_valid_dates_extra.append(weekend)
                        count = 0
                        break
                else:
                    count = 0

        leave_without_pay_valid_dates = leave_without_pay_valid_dates + leave_without_pay_valid_dates_extra






        leave_with_out_pay=float(len(leave_without_pay_valid_dates))
        # leave_with_out_pay = float(len(leave_with_out_pay_dates))
        leave_with_out_pay_hour=leave_with_out_pay*standard_work_hour
        return leave_with_out_pay_hour

    def get_leave_with_out_pay_datas(self, id, start_date, end_date):
        user_timezone = int(fields.datetime.now(pytz.timezone(self.env.user.tz or 'GMT')).strftime("%Z"))
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        leave_with_out_pay_dates = []
        month = start_date.month
        year = end_date.year
        query = """select date_from,date_to  from hr_leave  where  ((date_from::DATE between '{}'::DATE and '{}'::DATE) or (date_to::DATE between '{}'::DATE and '{}'::date)) 
           and type_for='{}' and employee_id={} and state='{}'""".format(
            start_date, end_date, start_date, end_date, 'leave_with_out_pay', id, 'validate')
        self._cr.execute(query)

        get_leave_with_out_pay_result = self._cr.fetchall()
        for result in get_leave_with_out_pay_result:
            # date_from = result[12].date()
            # date_to = end_date
            # if result[13].date() < end_date:
            #     date_to = result[13].date()
            # if date_from == date_to:
            #     if date_from not in leave_with_out_pay_dates:
            #         leave_with_out_pay_dates.append(date_from)
            result_list = list(result)
            result_list[0] = result_list[0] + datetime.timedelta(hours=user_timezone)
            date_from = result_list[0].date()
            result_list[1] = result_list[1] + datetime.timedelta(hours=user_timezone)
            date_to = result_list[1].date()
            # date_to = end_date
            if result_list[1].date() < end_date and result_list[0].date() < start_date:
                date_to = end_date
            if result_list[0].date() < start_date:
                date_from = start_date
            if result_list[1].date() > end_date:
                date_to = end_date
            if date_from == date_to:
                if date_from not in leave_with_out_pay_dates:
                    leave_with_out_pay_dates.append(date_from)
            else:
                # count=0
                if date_from.day > date_to.day:
                    date_from = start_date
                for day in range(date_from.day, date_to.day + 1):
                    # generate_date = start_date + relativedelta(days=day) - relativedelta(days=start_date.day)
                    generate_date = start_date + relativedelta(days=day) - relativedelta(days=start_date.day)
                    if generate_date not in leave_with_out_pay_dates:
                        leave_with_out_pay_dates.append(generate_date)
        ##********************get works dates********************##
        worked_dates = []
        if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
            work_days_time = self.env['hr.work.entry'].sudo().search(
                [('employee_id', '=', id), ('date_start', '>=', start_date),
                 ('date_start', '<=', end_date)])

            # for line in monthly_total_work_details:
            #     worked_dates.append(line.date_start)


        else:
            work_days_time = self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', start_date),
                 ('date', '<=', end_date)])

        monthly_total_work_hour = 0
        monthly_not_hour = 0
        work_date_dict = dict()
        for time in work_days_time:
            if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                if time.date_start.date() not in work_date_dict.keys():
                    work_date_dict[time.date_start.date()] = time.duration
                else:
                    work_date_dict[time.date_start.date()] += time.duration
            else:
                if time.date not in work_date_dict.keys():
                    work_date_dict[time.date] = time.unit_amount
                else:
                    work_date_dict[time.date] += time.unit_amount

        for time in work_date_dict.keys():
            if work_date_dict[time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                monthly_total_work_hour += work_date_dict[time]
            else:
                monthly_not_hour += work_date_dict[
                                        time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

            # for line in monthly_total_work_details:
            #     worked_dates.append(line.date)

        ##********************get works dates********************##
        # if leave without pay fall in already worked day**********************
        leave_with_out_pay = 0.0
        leave_without_pay_valid_dates = []
        for leave in leave_with_out_pay_dates:
            if leave not in work_date_dict.keys() or (leave in work_date_dict.keys() and work_date_dict[leave] == 0):
                leave_with_out_pay += 1
                leave_without_pay_valid_dates.append(leave)

        # copy_leave_without_pay_valid_dates=leave_without_pay_valid_dates

        # if leave without pay fall in already worked day**********************
        # if leave without pay fall in weekend**********************************
        c = calendar.Calendar()

        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        weekend = self.env['week.day']
        if self.contract_id.weekend_day:
            weekend = self.contract_id.weekend_day
        else:
            weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
        monthcal = c.monthdatescalendar(year, month)
        weekend_day = []
        # weekend_day.append(calendar.SUNDAY)
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
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        weekend_date_this_month = []
        for date in dates:
            day_num = date.weekday()
            # day = calendar.day_name[day_num]
            if day_num in weekend_day:
                weekend_date_this_month.append(date)

        # if len(weekend_date_this_month) > 0:
        #     for leave in leave_without_pay_valid_dates:
        #         if leave in weekend_date_this_month:
        #             leave_without_pay_valid_dates.remove(leave)



        count = 0
        leave_without_pay_valid_dates_extra = []
        for weekend in weekend_date_this_month:
            for leave in leave_without_pay_valid_dates:
                if abs(weekend.day - leave.day) == 1:
                    # leave_without_pay_valid_dates_extra.append(weekend)
                    # break
                    count += 1
                    if count == 2:
                        leave_without_pay_valid_dates_extra.append(weekend)
                        count = 0
                        break
                else:
                    count = 0

        leave_without_pay_valid_dates = leave_without_pay_valid_dates + leave_without_pay_valid_dates_extra


        return leave_without_pay_valid_dates

    def food_allowance(self,id,start_date,end_date):
        actual_need_to_work,bt_emp_work=self.emp_monthly_work_history_for_allowance(id,start_date,end_date)
        if bt_emp_work>actual_need_to_work:
            return self.contract_id.food_allowance
        else:
            diff=actual_need_to_work-bt_emp_work
            food_allwnce_should_be=(self.contract_id.food_allowance*bt_emp_work)/actual_need_to_work
            return round(food_allwnce_should_be,2)
        return 0

    def telephone_allowance(self,id,start_date,end_date):
        actual_need_to_work,bt_emp_work=self.emp_monthly_work_history_for_allowance(id,start_date,end_date)
        if bt_emp_work>actual_need_to_work:
            return self.contract_id.telephone_allowance
        else:
            diff=actual_need_to_work-bt_emp_work
            tel_allwnce_should_be=(self.contract_id.telephone_allowance*bt_emp_work)/actual_need_to_work
            return round(tel_allwnce_should_be,2)
        return 0

    def vehicle_allowance(self,id,start_date,end_date):
        actual_need_to_work,bt_emp_work=self.emp_monthly_work_history_for_allowance(id,start_date,end_date)
        if bt_emp_work>actual_need_to_work:
            return self.contract_id.vehicle_allowance
        else:
            diff=actual_need_to_work-bt_emp_work
            vehicle_allwnce_should_be=(self.contract_id.vehicle_allowance*bt_emp_work)/actual_need_to_work
            return round(vehicle_allwnce_should_be,2)
        return 0

    def other_allowance(self,id,start_date,end_date):
        actual_need_to_work,bt_emp_work=self.emp_monthly_work_history_for_allowance(id,start_date,end_date)
        if bt_emp_work>actual_need_to_work:
            return self.contract_id.other_allowance
        else:
            diff=actual_need_to_work-bt_emp_work
            other_allwnce_should_be=(self.contract_id.other_allowance*bt_emp_work)/actual_need_to_work
            return round(other_allwnce_should_be,2)
        return 0

    def emp_monthly_work_history_for_allowance(self,id,start_date, end_date):
        leave_with_pay_hours = self.get_leave_with_pay(id, start_date, end_date)
        leave_with_out_pay_hours = self.get_leave_with_out_pay(id, start_date, end_date)
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        c = calendar.Calendar()

        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        weekend = self.env['week.day']
        if self.contract_id.weekend_day:
            weekend = self.contract_id.weekend_day
        else:
            weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
        monthcal = c.monthdatescalendar(year, month)
        weekend_day = []
        # weekend_day.append(calendar.SUNDAY)
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
        # no_of_weekend=0
        # for week in monthcal:
        #     for day in week:
        #         if
        number_of_weekday = len([day for week in monthcal for day in week if \
                                 day.weekday() in weekend_day and \
                                 day.month == month])

        # monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
        #     [('employee_id', '=', id), ('date', '>=', start_date),
        #      ('date', '<=', end_date)]).mapped('unit_amount'))
        if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
            work_days_time  = sum(self.env['hr.work.entry'].sudo().search(
                [('employee_id', '=', id), ('date_start', '>=', start_date),
                 ('date_start', '<=', end_date)]).mapped('duration'))
        else:
            work_days_time  = sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', start_date),
                 ('date', '<=', end_date)]).mapped('unit_amount'))
        monthly_total_work_hour = 0
        monthly_not_hour = 0
        work_date_dict = dict()
        for time in work_days_time:
            if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                if time.date_start.date() not in work_date_dict.keys():
                    work_date_dict[time.date_start.date()] = time.duration
                else:
                    work_date_dict[time.date_start.date()] += time.duration
            else:
                if time.date not in work_date_dict.keys():
                    work_date_dict[time.date] = time.unit_amount
                else:
                    work_date_dict[time.date] += time.unit_amount

        for time in work_date_dict.keys():
            if work_date_dict[time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                monthly_total_work_hour += work_date_dict[time]
            else:
                monthly_not_hour += work_date_dict[
                                        time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

        #######PUBLIC HOLIDAY###########
        ph_day = 0
        public_holidays = self.env['hr.leave'].sudo().search(
            [('mode_company_id', '=', self.company_id.id),
             ('date_from', '>=', start_date), ('date_to', '<=', end_date), ('state', '=', 'validate')],
            order='date_from')

        # CALCULATION OF WEEKEND WORK HOUR
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        weekend_date_this_month = []
        for date in dates:
            day_num = date.weekday()
            # day = calendar.day_name[day_num]
            if day_num in weekend_day:
                weekend_date_this_month.append(date)
        public_holiday_work_hour = 0
        public_holiday_only = 0
        if weekend_date_this_month:
            for date in weekend_date_this_month:
                min_time = datetime.datetime.min.time()
                max_time = datetime.datetime.max.time()
                my_min_datetime = datetime.datetime.combine(date, min_time)
                my_max_datetime = datetime.datetime.combine(date, max_time)

                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.id), ('date', '>=', my_min_datetime),
                     ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
        # CALCULATION OF WEEKEND WORK HOUR
        public_holiday_dates = []
        for holiday in public_holidays:
            from_date = holiday.date_from
            to_date = holiday.date_to.date()
            delta = to_date - from_date.date()
            for i in range(delta.days + 1):
                day = from_date + datetime.timedelta(days=i)
                public_holiday_dates.append(day.date())
            public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', holiday.date_from),
                 ('date', '<=', holiday.date_to)]).mapped('unit_amount'))
            public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', holiday.date_from),
                 ('date', '<=', holiday.date_to)]).mapped('unit_amount'))
            ph_day += holiday.number_of_days
        #######PUBLIC HOLIDAY###########

        date_need_to_remove_from_holiday = 0
        work_hour_need_to_remove = 0
        if len(public_holiday_dates) > 0:
            for weekend_date in weekend_date_this_month:
                if weekend_date in public_holiday_dates:
                    date_need_to_remove_from_holiday += 1
                    work_hour_need_to_remove += sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', id), ('date', '=', weekend_date)]).mapped('unit_amount'))
            ph_day -= date_need_to_remove_from_holiday
        net_working_day = calendar_days - number_of_weekday - ph_day
        net_working_hour = round(
            calendar_days * standard_work_hour - number_of_weekday * standard_work_hour - ph_day * standard_work_hour,
            2)
        HOT_day = ph_day
        # HOT_Hour = round(ph_day * standard_work_hour, 2)
        HOT_Hour = round(public_holiday_work_hour, 2) - round(work_hour_need_to_remove, 2)
        monthly_total_day = monthly_total_work_hour / standard_work_hour
        monthly_total_hour = round(monthly_total_work_hour, 2)
        net_worked_day = monthly_total_day - HOT_day
        net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)

        actual_need_to_work = net_working_hour
        but_emp_work = monthly_total_work_hour - HOT_Hour
        return actual_need_to_work,but_emp_work

    def employee_monthly_work_history(self,id,start_date, end_date):
        if self.contract_id.structure_type_id.default_struct_id.overtime_cal_method=='on_monthly':
            leave_with_pay_hours=self.get_leave_with_pay(id,start_date, end_date)
            leave_with_out_pay_hours=self.get_leave_with_out_pay(id,start_date, end_date)
            standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
            c = calendar.Calendar()

            year = start_date.year
            month = start_date.month
            calendar_day = calendar.monthrange(year, month)
            calendar_days = calendar_day[1]
            weekend = self.env['week.day']
            if self.contract_id.weekend_day:
                weekend = self.contract_id.weekend_day
            else:
                weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
            monthcal = c.monthdatescalendar(year, month)
            weekend_day = []
            # weekend_day.append(calendar.SUNDAY)
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
            # no_of_weekend=0
            # for week in monthcal:
            #     for day in week:
            #         if
            number_of_weekday = len([day for week in monthcal for day in week if \
                                     day.weekday() in weekend_day and \
                                     day.month == month])

            # monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
            #     [('employee_id', '=', id), ('date', '>=', start_date),
            #      ('date', '<=', end_date)]).mapped('unit_amount'))
            if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                monthly_total_work_hour = sum(self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', id), ('date_start', '>=', start_date),
                     ('date_start', '<=', end_date)]).mapped('duration'))
            else:
                monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', start_date),
                     ('date', '<=', end_date)]).mapped('unit_amount'))

            #######PUBLIC HOLIDAY###########
            ph_day = 0
            public_holidays = self.env['hr.leave'].sudo().search(
                [('mode_company_id', '=', self.company_id.id),
                 ('date_from', '>=', start_date), ('date_to', '<=', end_date),('state','=','validate')], order='date_from')

            # CALCULATION OF WEEKEND WORK HOUR
            num_days = calendar.monthrange(year, month)[1]
            dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
            weekend_date_this_month = []
            for date in dates:
                day_num = date.weekday()
                # day = calendar.day_name[day_num]
                if day_num in weekend_day:
                    weekend_date_this_month.append(date)
            public_holiday_work_hour = 0
            public_holiday_only = 0
            if weekend_date_this_month:
                for date in weekend_date_this_month:
                    min_time = datetime.datetime.min.time()
                    max_time = datetime.datetime.max.time()
                    my_min_datetime = datetime.datetime.combine(date, min_time)
                    my_max_datetime = datetime.datetime.combine(date, max_time)

                    public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', self.id), ('date', '>=', my_min_datetime),
                         ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
            # CALCULATION OF WEEKEND WORK HOUR
            public_holiday_dates = []
            for holiday in public_holidays:
                from_date = holiday.date_from + datetime.timedelta(hours=6)
                to_date = holiday.date_to + datetime.timedelta(hours=6)
                delta = to_date.date() - from_date.date()
                for i in range(delta.days + 1):
                    day = from_date + datetime.timedelta(days=i)
                    public_holiday_dates.append(day.date())
                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))
                public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))
                ph_day += holiday.number_of_days
            #######PUBLIC HOLIDAY###########

            ####################Leave with pay####################
            # leave_with_pay_dates = []
            # month = start_date.month
            # year = end_date.year
            # query = """select date_from,date_to  from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}'""".format(
            #     start_date, month, end_date, year, 'leave_with_pay')
            # self._cr.execute(query)
            #
            # get_leave_with_pay_result = self._cr.fetchall()
            # for result in get_leave_with_pay_result:
            #     date = result[12].date()
            #     # if datetime.strptime(result['date_from'],DATE_FORMAT)>self.date_to:
            #     #     break;
            #     # else:
            #     if date == end_date:
            #         if date not in leave_with_pay_dates:
            #             leave_with_pay_dates.append(date)
            #     else:
            #         # count=0
            #         for day in range(date.day, end_date.day + 1):
            #             generate_date = start_date + relativedelta(days=day) - relativedelta(
            #                 days=start_date.day)
            #             if generate_date not in leave_with_pay_dates:
            #                 leave_with_pay_dates.append(generate_date)
            #
            # leave_with_pay = float(len(leave_with_pay_dates))
            # leave_with_pay_hour=leave_with_pay*standard_work_hour
            ####################Leave with pay####################
            date_need_to_remove_from_holiday = 0
            work_hour_need_to_remove = 0
            if len(public_holiday_dates) > 0:
                for weekend_date in weekend_date_this_month:
                    if weekend_date in public_holiday_dates:
                        date_need_to_remove_from_holiday += 1
                        work_hour_need_to_remove += sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', id), ('date', '=', weekend_date)]).mapped('unit_amount'))
                ph_day -= date_need_to_remove_from_holiday
            net_working_day = calendar_days - number_of_weekday -ph_day
            net_working_hour = round(calendar_days * standard_work_hour - number_of_weekday * standard_work_hour-ph_day*standard_work_hour, 2)
            HOT_day = ph_day
            # HOT_Hour = round(ph_day * standard_work_hour, 2)
            HOT_Hour = round(public_holiday_work_hour, 2)-round(work_hour_need_to_remove,2)
            monthly_total_day = monthly_total_work_hour / standard_work_hour
            monthly_total_hour = round(monthly_total_work_hour, 2)
            net_worked_day = monthly_total_day - HOT_day
            net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)

            actual_need_to_work = net_working_hour
            but_emp_work = monthly_total_work_hour - HOT_Hour
            time_work = 0
            # if but_emp_work > actual_need_to_work:
            time_work = but_emp_work - actual_need_to_work

            # not_day = net_worked_day-net_working_day+(leave_with_out_pay_hours/standard_work_hour)+(leave_with_pay_hours/standard_work_hour)
            # not_hour=not_day*standard_work_hour
            not_hour = time_work
            not_day = time_work / 8
            # if leave_with_pay>0:
            #     if not_hour<0:
            #         not_hour=not_hour+leave_with_pay_hour
            #     else:
            #         not_hour = not_hour - leave_with_pay_hour
            # *************************
            # if not_hour<0:
            #     not_hour=(-1)*not_hour
            # *************************
                # not_hour=not_hour+leave_with_out_pay_hours+leave_with_pay_hours
            return not_hour,HOT_Hour
        else:
            leave_with_pay_hours = self.get_leave_with_pay(id, start_date, end_date)
            leave_with_out_pay_hours = self.get_leave_with_out_pay(id, start_date, end_date)
            leave_with_out_pay_datas = self.get_leave_with_out_pay_datas(id, start_date, end_date)
            standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
            c = calendar.Calendar()

            year = start_date.year
            month = start_date.month
            calendar_day = calendar.monthrange(year, month)
            calendar_days = calendar_day[1]
            weekend = self.env['week.day']
            if self.contract_id.weekend_day:
                weekend = self.contract_id.weekend_day
            else:
                weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
            monthcal = c.monthdatescalendar(year, month)
            weekend_day = []
            # weekend_day.append(calendar.SUNDAY)
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
            # no_of_weekend=0
            # for week in monthcal:
            #     for day in week:
            #         if
            number_of_weekday = len([day for week in monthcal for day in week if \
                                     day.weekday() in weekend_day and \
                                     day.month == month])
            number_of_weekday_actual=len([day for week in monthcal for day in week if \
                                     day.weekday() in weekend_day and \
                                     day.month == month])

            weekday_dates = [day for week in monthcal for day in week if \
                             day.weekday() in weekend_day and \
                             day.month == month]

            public_holidays = self.env['hr.leave'].sudo().search(
                [('mode_company_id', '=', self.company_id.id),
                 ('date_from', '>=', start_date), ('date_to', '<=', end_date), ('state', '=', 'validate')],
                order='date_from')

            public_holiday_dates = []
            for holiday in public_holidays:
                from_date = holiday.date_from + datetime.timedelta(hours=6)
                to_date = holiday.date_to + datetime.timedelta(hours=6)
                delta = to_date.date() - from_date.date()
                for i in range(delta.days + 1):
                    day = from_date + datetime.timedelta(days=i)
                    public_holiday_dates.append(day.date())

            for leave in leave_with_out_pay_datas:
                for weekend in weekday_dates:
                    if weekend not in public_holiday_dates and leave==weekend:
                        weekday_dates.remove(leave)
            number_of_weekday=len(weekday_dates)

            weekday_not_consider=number_of_weekday_actual-number_of_weekday
            extra_weekday = 0
            extra_weekhour = 0
            if weekday_not_consider>0:
                extra_weekday=weekday_not_consider
                extra_weekhour=weekday_not_consider*standard_work_hour
            # number_of_weekday_actual = len([day for week in monthcal for day in week if \
            #                                 day.weekday() in weekend_day and \
            #                                 day.month == month])
            #
            # for leave in leave_with_out_pay_datas:
            #     for weekend in weekday_dates:
            #         if leave==weekend:
            #             weekday_dates.remove(leave)
            # number_of_weekday=len(weekday_dates)
            #
            # weekday_not_consider = number_of_weekday_actual - number_of_weekday
            # extra_weekday = 0
            # extra_weekhour = 0
            # if weekday_not_consider > 0:
            #     extra_weekday = weekday_not_consider
            #     extra_weekhour = weekday_not_consider * standard_work_hour

            # monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
            #     [('employee_id', '=', id), ('date', '>=', start_date),
            #      ('date', '<=', end_date)]).mapped('unit_amount'))
            if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                monthly_total_work_hour = sum(self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', id), ('date_start', '>=', start_date),
                     ('date_start', '<=', end_date)]).mapped('duration'))
            else:
                work_days_time = self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', start_date),
                     ('date', '<=', end_date), ('date', 'not in', weekday_dates)])
                monthly_total_work_hour = 0
                monthly_not_hour = 0
                work_date_dict=dict()
                for time in work_days_time:
                    if self.contract_id.structure_type_id.default_struct_id.structure_type == 'basic_pay_office_stuff':
                        if time.date_start.date() not in work_date_dict.keys():
                            work_date_dict[time.date_start.date()] = time.duration
                        else:
                            work_date_dict[time.date_start.date()] += time.duration
                    else:
                        if time.date not in work_date_dict.keys():
                            work_date_dict[time.date] = time.unit_amount
                        else:
                            work_date_dict[time.date] += time.unit_amount

                # for time in work_date_dict.keys():
                #     if work_date_dict[time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                #         monthly_total_work_hour += work_date_dict[time]
                #     else:
                #         monthly_not_hour += work_date_dict[time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                #         monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour



                monthly_actual_timesheet_hour = sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', start_date),
                     ('date', '<=', end_date)]).mapped('unit_amount'))
            #######PUBLIC HOLIDAY###########
            ph_day = 0
            public_holidays = self.env['hr.leave'].sudo().search(
                [('mode_company_id', '=', self.company_id.id),
                 ('date_from', '>=', start_date), ('date_to', '<=', end_date), ('state', '=', 'validate')],
                order='date_from')

            # CALCULATION OF WEEKEND WORK HOUR
            num_days = calendar.monthrange(year, month)[1]
            dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
            weekend_date_this_month = []
            for date in dates:
                day_num = date.weekday()
                # day = calendar.day_name[day_num]
                if day_num in weekend_day:
                    weekend_date_this_month.append(date)
            public_holiday_work_hour = 0
            public_holiday_only = 0
            if weekend_date_this_month:
                for date in weekend_date_this_month:
                    min_time = datetime.datetime.min.time()
                    max_time = datetime.datetime.max.time()
                    my_min_datetime = datetime.datetime.combine(date, min_time)
                    my_max_datetime = datetime.datetime.combine(date, max_time)

                    public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', self.id), ('date', '>=', my_min_datetime),
                         ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
            # CALCULATION OF WEEKEND WORK HOUR
            public_holiday_dates = []
            for holiday in public_holidays:
                from_date = holiday.date_from + datetime.timedelta(hours=6)
                to_date = holiday.date_to + datetime.timedelta(hours=6)
                delta = to_date.date() - from_date.date()
                for i in range(delta.days + 1):
                    day = from_date + datetime.timedelta(days=i)
                    public_holiday_dates.append(day.date())
                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))
                public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))
                ph_day += holiday.number_of_days
            #######PUBLIC HOLIDAY###########

            for time in work_date_dict.keys():
                if time not in public_holiday_dates:
                    print(monthly_total_work_hour)
                    if work_date_dict[
                        time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                        monthly_total_work_hour += work_date_dict[time]
                    else:
                        monthly_not_hour += work_date_dict[
                                                time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                        monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

            ####################Leave with pay####################
            # leave_with_pay_dates = []
            # month = start_date.month
            # year = end_date.year
            # query = """select date_from,date_to  from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}'""".format(
            #     start_date, month, end_date, year, 'leave_with_pay')
            # self._cr.execute(query)
            #
            # get_leave_with_pay_result = self._cr.fetchall()
            # for result in get_leave_with_pay_result:
            #     date = result[12].date()
            #     # if datetime.strptime(result['date_from'],DATE_FORMAT)>self.date_to:
            #     #     break;
            #     # else:
            #     if date == end_date:
            #         if date not in leave_with_pay_dates:
            #             leave_with_pay_dates.append(date)
            #     else:
            #         # count=0
            #         for day in range(date.day, end_date.day + 1):
            #             generate_date = start_date + relativedelta(days=day) - relativedelta(
            #                 days=start_date.day)
            #             if generate_date not in leave_with_pay_dates:
            #                 leave_with_pay_dates.append(generate_date)
            #
            # leave_with_pay = float(len(leave_with_pay_dates))
            # leave_with_pay_hour=leave_with_pay*standard_work_hour
            ####################Leave with pay####################
            date_need_to_remove_from_holiday = 0
            work_hour_need_to_remove = 0
            if len(public_holiday_dates) > 0:
                for weekend_date in weekend_date_this_month:
                    if weekend_date in public_holiday_dates:
                        date_need_to_remove_from_holiday += 1
                        work_hour_need_to_remove += sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', id), ('date', '=', weekend_date)]).mapped('unit_amount'))
                ph_day -= date_need_to_remove_from_holiday
            net_working_hour = round(
                calendar_days * standard_work_hour - number_of_weekday * standard_work_hour-weekday_not_consider*standard_work_hour - ph_day * standard_work_hour,
                2)
            # HOT_Hour = round(ph_day * standard_work_hour, 2)
            HOT_Hour = round(public_holiday_work_hour, 2) - round(work_hour_need_to_remove, 2)

            net_worked_hour = round(monthly_total_work_hour, 2)
            not_hour = round(monthly_not_hour, 2)

            if net_working_hour > net_worked_hour:
                absent_hour = abs(round(net_working_hour - net_worked_hour-leave_with_pay_hours-leave_with_out_pay_hours+extra_weekhour, 2))
            else:
                absent_hour=0

            return absent_hour, not_hour, HOT_Hour

    def get_public_holiday_weekend_dates(self,id,start_date, end_date):
        # if self.contract_id.structure_type_id.default_struct_id.overtime_cal_method=='on_monthly':
            # leave_with_pay_hours=self.get_leave_with_pay(id,start_date, end_date)
            # leave_with_out_pay_hours=self.get_leave_with_out_pay(id,start_date, end_date)
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        c = calendar.Calendar()

        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        weekend = self.env['week.day']
        if self.contract_id.weekend_day:
            weekend = self.contract_id.weekend_day
        else:
            weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
        monthcal = c.monthdatescalendar(year, month)
        weekend_day = []
        # weekend_day.append(calendar.SUNDAY)
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
        # no_of_weekend=0
        # for week in monthcal:
        #     for day in week:
        #         if
        number_of_weekday = len([day for week in monthcal for day in week if \
                                 day.weekday() in weekend_day and \
                                 day.month == month])

        # monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
        #     [('employee_id', '=', id), ('date', '>=', start_date),
        #      ('date', '<=', end_date)]).mapped('unit_amount'))


        #######PUBLIC HOLIDAY###########
        ph_day = 0
        public_holidays = self.env['hr.leave'].sudo().search(
            [('mode_company_id', '=', self.company_id.id),
             ('date_from', '>=', start_date), ('date_to', '<=', end_date),('state','=','validate')], order='date_from')

        # CALCULATION OF WEEKEND WORK HOUR
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        weekend_date_this_month = []
        for date in dates:
            day_num = date.weekday()
            # day = calendar.day_name[day_num]
            if day_num in weekend_day:
                weekend_date_this_month.append(date)
        public_holiday_work_hour = 0
        public_holiday_only = 0
        if weekend_date_this_month:
            for date in weekend_date_this_month:
                min_time = datetime.datetime.min.time()
                max_time = datetime.datetime.max.time()
                my_min_datetime = datetime.datetime.combine(date, min_time)
                my_max_datetime = datetime.datetime.combine(date, max_time)

                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.id), ('date', '>=', my_min_datetime),
                     ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
        # CALCULATION OF WEEKEND WORK HOUR
        public_holiday_dates = []
        for holiday in public_holidays:
            from_date = holiday.date_from + datetime.timedelta(hours=6)
            to_date = holiday.date_to + datetime.timedelta(hours=6)
            delta = to_date.date() - from_date.date()
            for i in range(delta.days + 1):
                day = from_date + datetime.timedelta(days=i)
                public_holiday_dates.append(day.date())
            public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', from_date),
                 ('date', '<=', to_date)]).mapped('unit_amount'))
            public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', id), ('date', '>=', from_date),
                 ('date', '<=', to_date)]).mapped('unit_amount'))
            ph_day += holiday.number_of_days
        #######PUBLIC HOLIDAY###########

        ####################Leave with pay####################
        # leave_with_pay_dates = []
        # month = start_date.month
        # year = end_date.year
        # query = """select date_from,date_to  from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}'""".format(
        #     start_date, month, end_date, year, 'leave_with_pay')
        # self._cr.execute(query)
        #
        # get_leave_with_pay_result = self._cr.fetchall()
        # for result in get_leave_with_pay_result:
        #     date = result[12].date()
        #     # if datetime.strptime(result['date_from'],DATE_FORMAT)>self.date_to:
        #     #     break;
        #     # else:
        #     if date == end_date:
        #         if date not in leave_with_pay_dates:
        #             leave_with_pay_dates.append(date)
        #     else:
        #         # count=0
        #         for day in range(date.day, end_date.day + 1):
        #             generate_date = start_date + relativedelta(days=day) - relativedelta(
        #                 days=start_date.day)
        #             if generate_date not in leave_with_pay_dates:
        #                 leave_with_pay_dates.append(generate_date)
        #
        # leave_with_pay = float(len(leave_with_pay_dates))
        # leave_with_pay_hour=leave_with_pay*standard_work_hour
        ####################Leave with pay####################
        date_need_to_remove_from_holiday = 0
        work_hour_need_to_remove = 0
        if len(public_holiday_dates) > 0:
            for weekend_date in weekend_date_this_month:
                if weekend_date in public_holiday_dates:
                    date_need_to_remove_from_holiday += 1
                    work_hour_need_to_remove += sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', id), ('date', '=', weekend_date)]).mapped('unit_amount'))
            ph_day -= date_need_to_remove_from_holiday
        net_working_day = calendar_days - number_of_weekday -ph_day
        net_working_hour = round(calendar_days * standard_work_hour - number_of_weekday * standard_work_hour-ph_day*standard_work_hour, 2)
        HOT_day = ph_day
        # HOT_Hour = round(ph_day * standard_work_hour, 2)
        HOT_Hour = round(public_holiday_work_hour, 2)-round(work_hour_need_to_remove,2)

        return weekend_date_this_month,public_holiday_dates


    def get_half_day_details(self, id, start_date, end_date):
        leave_without_pay_dates=self.get_leave_with_out_pay_datas(id, start_date, end_date)
        leave_with_pay_dates=self.get_leave_with_pay_dates(id, start_date, end_date)
        weekend_dates,public_holiday_dates=self.get_public_holiday_weekend_dates(id, start_date, end_date)

        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        c = calendar.Calendar()
        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        get_half_day = self.contract_id.structure_type_id.default_struct_id.half_day
        if self.contract_id.half_day:
            get_half_day = self.contract_id.half_day
        half_day_date_this_month = []
        monthcal = c.monthdatescalendar(year, month)
        number_of_half_day=0
        actual_half_day_need_to_work=0
        get_work_duration_half_days=0
        get_pay_hour=0
        if get_half_day:
            half_day = []
            # weekend_day.append(calendar.SUNDAY)
            for wd in get_half_day:
                if wd.name == 'SATURDAY':
                    half_day.append(calendar.SATURDAY)
                if wd.name == 'SUNDAY':
                    half_day.append(calendar.SUNDAY)
                if wd.name == 'MONDAY':
                    half_day.append(calendar.MONDAY)
                if wd.name == 'TUESDAY':
                    half_day.append(calendar.TUESDAY)
                if wd.name == 'WEDNESDAY':
                    half_day.append(calendar.WEDNESDAY)
                if wd.name == 'THURSDAY':
                    half_day.append(calendar.THURSDAY)
                if wd.name == 'FRIDAY':
                    half_day.append(calendar.FRIDAY)

            number_of_half_day = len([day for week in monthcal for day in week if \
                                      day.weekday() in half_day and \
                                      day.month == month])
            num_days = calendar.monthrange(year, month)[1]
            dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
            for date in dates:
                day_num = date.weekday()
                # day = calendar.day_name[day_num]
                if day_num in half_day:
                    half_day_date_this_month.append(date)

            need_to_remove_have_date=[]
            if half_day_date_this_month:
                for h_date in half_day_date_this_month:
                    if h_date in leave_with_pay_dates or h_date in leave_without_pay_dates or h_date in public_holiday_dates or h_date in weekend_dates:
                        # half_day_date_this_month.remove(h_date)
                        need_to_remove_have_date.append(h_date)
            if need_to_remove_have_date:
                for r_date in need_to_remove_have_date:
                    half_day_date_this_month.remove(r_date)
            number_of_half_day=len(half_day_date_this_month)

            get_work_duration_half_days=0
            for half_date in half_day_date_this_month:
                get_work_duration_half_days += sum(self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', id), ('date_start', '>=', half_date), ('date_start', '<=', half_date)]).mapped("duration"))

            actual_half_day_need_to_work=number_of_half_day*standard_work_hour

            get_pay_hour=actual_half_day_need_to_work-get_work_duration_half_days


        return number_of_half_day,actual_half_day_need_to_work,get_work_duration_half_days,get_pay_hour