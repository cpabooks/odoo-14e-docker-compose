import calendar
import datetime

from dateutil.relativedelta import relativedelta
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, Payslips, WorkedDays, InputLine
from odoo import models, fields, api,_
from odoo.tools import format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_custom_working_days_inputs(self):
        self.custom_working_days_inputs = [(5, 0, 0)]
        # fill only if the contract as a working schedule linked
        self.ensure_one()

        standard_work_hour = self.struct_id.standard_working_hour
        c = calendar.Calendar()

        year = self.date_from.year
        month = self.date_from.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]
        weekend = self.env['week.day']
        if self.contract_id.weekend_day:
            weekend = self.contract_id.weekend_day
        else:
            weekend = self.struct_id.weekend_day
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

        number_of_weekday = len([day for week in monthcal for day in week if \
                                 day.weekday() in weekend_day and \
                                 day.month == month])
        weekday_dates=[day for week in monthcal for day in week if \
                                 day.weekday() in weekend_day and \
                                 day.month == month]

        if self.struct_id.structure_type == 'basic_pay_office_stuff':
            monthly_total_work_hour = sum(self.env['hr.work.entry'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                 ('date_start', '<=', self.date_to)]).mapped('duration'))
            count_day_monthly_total_work_hour = self.env['hr.work.entry'].sudo().search_count(
                [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                 ('date_start', '<=', self.date_to)])

        else:
            work_days_time=self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                 ('date', '<=', self.date_to),('date','not in',weekday_dates)])
            monthly_total_work_hour=0
            monthly_not_hour=0
            for time in work_days_time:
                if time.unit_amount<=self.struct_id.standard_working_hour:
                    monthly_total_work_hour+=time.unit_amount
                else:
                    monthly_not_hour+=time.unit_amount-self.struct_id.standard_working_hour
                    monthly_total_work_hour +=self.struct_id.standard_working_hour
            #     print("***")
            monthly_actual_timesheet_hour = sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                 ('date', '<=', self.date_to)]).mapped('unit_amount'))
            # count_day_monthly_total_work_hour = self.env['account.analytic.line'].sudo().search_count(
            #     [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
            #      ('date', '<=', self.date_to)])
        #######PUBLIC HOLIDAY###########
        ph_day = 0
        public_holidays = self.env['hr.leave'].sudo().search(
            [('mode_company_id', '=', self.contract_id.employee_id.company_id.id),
             ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)], order='date_from')

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
        weekend_work_hour = 0
        public_holiday_only = 0
        if weekend_date_this_month:
            for date in weekend_date_this_month:
                min_time = datetime.datetime.min.time()
                max_time = datetime.datetime.max.time()
                my_min_datetime = datetime.datetime.combine(date, min_time)
                my_max_datetime = datetime.datetime.combine(date, max_time)

                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date', '>=', my_min_datetime),
                     ('date', '<=', my_max_datetime)]).mapped('unit_amount'))
        # CALCULATION OF WEEKEND WORK HOUR
        public_holiday_dates = []

        for holiday in public_holidays:
            # need to remove weekend date from here
            from_date = holiday.date_from + datetime.timedelta(hours=6)
            to_date = holiday.date_to + datetime.timedelta(hours=6)
            delta = to_date.date() - from_date.date()
            for i in range(delta.days + 1):
                day = from_date + datetime.timedelta(days=i)
                public_holiday_dates.append(day.date())

            public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('date', '>=', from_date),
                 ('date', '<=', to_date)]).mapped('unit_amount'))
            public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('date', '>=', from_date),
                 ('date', '<=', to_date)]).mapped('unit_amount'))

            ph_day += holiday.number_of_days
        date_need_to_remove_from_holiday = 0
        work_hour_need_to_remove = 0
        if len(public_holiday_dates) > 0:
            for weekend_date in weekend_date_this_month:
                if weekend_date in public_holiday_dates:
                    date_need_to_remove_from_holiday += 1
                    work_hour_need_to_remove += sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', self.employee_id.id), ('date', '=', weekend_date)]).mapped('unit_amount'))
            ph_day -= date_need_to_remove_from_holiday

        #######PUBLIC HOLIDAY###########
        #######Leave With Pay###########
        # leave_with_pay_dates=[]
        # month=self.date_from.month
        # year=self.date_from.year
        # query="""select * from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}' and employee_id={} and state='{}'""".format(self.date_from,month,self.date_from,year,'leave_with_pay',self.employee_id.id,'validate')
        # self._cr.execute(query)
        #
        # get_leave_with_pay_result=self._cr.fetchall()
        # for result in get_leave_with_pay_result:
        #     date_from=result[12].date()
        #     date_to= self.date_to
        #     leave_date_to=result[13].date()
        #     if leave_date_to<self.date_to:
        #         date_to=result[13].date()
        #     if date_from == date_to:
        #         if date_from not in leave_with_pay_dates:
        #             leave_with_pay_dates.append(date_from)
        #     else:
        #         # count=0
        #         if date_from.day > date_to.day:
        #             date_from = self.date_to
        #         for day in range(date_from.day, date_to.day+1):
        #             generate_date=self.date_from + relativedelta(days=day) - relativedelta(days=self.date_from.day)
        #             if generate_date not in leave_with_pay_dates:
        #                 leave_with_pay_dates.append(generate_date)

        # leave_with_pay=float(len(leave_with_pay_dates))
        leave_with_pay_hour = self.employee_id.get_leave_with_pay(self.employee_id.id, self.date_from, self.date_to)
        leave_with_pay = leave_with_pay_hour / standard_work_hour
        #######Leave With Pay###########
        #######Leave With Out Pay###########
        # leave_with_out_pay_dates = []
        # month = self.date_from.month
        # year = self.date_from.year
        # query = """select * from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}' and employee_id={} and state='{}'""".format(
        #     self.date_from, month, self.date_from, year, 'leave_with_out_pay',self.employee_id.id,'validate')
        # self._cr.execute(query)
        #
        # get_leave_with_out_pay_dates = self._cr.fetchall()
        # for result in get_leave_with_out_pay_dates:
        #     date_from = result[12].date()
        #     date_to = self.date_to
        #     if result[13].date() < self.date_to:
        #         date_to = result[13].date()
        #     if date_from == date_to:
        #         if date_from not in leave_with_out_pay_dates:
        #             leave_with_out_pay_dates.append(date_from)
        #     else:
        #         # count=0
        #         if date_from.day > date_to.day:
        #             date_from = self.date_to
        #         for day in range(date_from.day, date_to.day + 1):
        #             generate_date = self.date_from + relativedelta(days=day) - relativedelta(days=self.date_from.day)
        #             if generate_date not in leave_with_out_pay_dates:
        #                 leave_with_out_pay_dates.append(generate_date)

        # leave_with_out_pay = float(len(leave_with_out_pay_dates))
        leave_with_out_pay_hour = self.employee_id.get_leave_with_out_pay(self.employee_id.id, self.date_from,
                                                                          self.date_to)
        leave_with_out_pay = leave_with_out_pay_hour / standard_work_hour

        #######Leave With Out Pay###########
        net_working_day = calendar_days - number_of_weekday - ph_day
        net_working_hour = round(
            calendar_days * standard_work_hour - number_of_weekday * standard_work_hour - ph_day * standard_work_hour,
            2)
        HOT_day = ph_day
        # HOT_Hour = round(ph_day * standard_work_hour, 2)
        HOT_Hour = round(public_holiday_work_hour, 2) - round(work_hour_need_to_remove, 2)

        monthly_total_day = monthly_actual_timesheet_hour / standard_work_hour
        monthly_total_hour = round(monthly_actual_timesheet_hour, 2)
        # monthly_total_day = monthly_total_work_hour / standard_work_hour
        # monthly_total_hour = round(monthly_total_work_hour, 2)

        net_worked_day = monthly_total_work_hour/ standard_work_hour
        net_worked_hour = round(monthly_total_work_hour,2)
        # net_worked_day = monthly_total_day - HOT_day
        # net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)

        actual_need_to_work = net_working_hour
        but_emp_work = monthly_total_work_hour - HOT_Hour
        extra_time_work = 0
        # if but_emp_work>actual_need_to_work:
        extra_time_work = but_emp_work - actual_need_to_work


        not_hour = round(monthly_not_hour,2)
        not_day = monthly_not_hour / standard_work_hour
        # not_hour = extra_time_work
        # not_day = extra_time_work / standard_work_hour
        # not_hour=weekend_work_hour
        # not_day=not_hour/8
        absent_hour=round(net_working_hour-net_worked_hour,2)
        absent_day=(net_working_hour-net_worked_hour)/standard_work_hour
        result = {}
        result['1'] = {
            'work_day_id': self.id,
            'work_day_type': "Calendar Working",
            'work_day_days': round(float(calendar_days), 2),
            'work_day_hour': round(calendar_days * standard_work_hour, 2),
            'work_day_formula': 'total calendar days x {} hrs'.format(standard_work_hour)

        }
        result['2'] = {
            'work_day_id': self.id,
            'work_day_type': "Weekend",
            'work_day_days': round(float(number_of_weekday), 2),
            'work_day_hour': round(number_of_weekday * standard_work_hour, 2),
            'work_day_formula': 'number of weekend days x {} hrs'.format(standard_work_hour)

        }
        result['3'] = {
            'work_day_id': self.id,
            'work_day_type': "Holiday",
            'work_day_days': round(float(HOT_day), 2),
            # 'work_day_hour': round(public_holiday_only, 2),
            'work_day_hour': round(HOT_day * standard_work_hour, 2),
            'work_day_formula': 'number of holiday days x {} hrs'.format(standard_work_hour)

        }
        result['4'] = {
            'work_day_id': self.id,
            'work_day_type': "Net Working (d/h)",
            'work_day_days': round(float(net_working_day), 2),
            'work_day_hour': round(net_working_hour, 2),
            'work_day_formula': 'calendar working (d/h) - weekend (d/h) - public working (d/h)'

        }

        result['5'] = {
            'work_day_id': self.id,
            'work_day_type': "Net Worked (d/h)",
            'work_day_days': round(net_worked_day, 2),
            'work_day_hour': round(net_worked_hour, 2),
            'work_day_formula': 'acutal ts duration (d/h) - weekend (d/h) - public working (d/h)'

        }
        if self.struct_id.structure_type == 'basic_pay_office_stuff':
            result['6'] = {
                'work_day_id': self.id,
                'work_day_type': "Actual WE Duration (d/h)",
                'work_day_days': round(monthly_total_day, 2),
                'work_day_hour': round(monthly_total_hour, 2),
                'work_day_formula': 'from work entry : std (d/h) + worked in weekend (d/h) + worked in public working (d/h)'
            }
        else:
            result['6'] = {
                'work_day_id': self.id,
                'work_day_type': "Actual Timesheet Duration (d/h)",
                'work_day_days': round(monthly_total_day, 2),
                'work_day_hour': round(monthly_total_hour, 2),
                'work_day_formula': 'from timesheet : std (d/h) + worked in weekend (d/h) + worked in public working (d/h)'
            }

        result['7'] = {
            'work_day_id': self.id,
            'work_day_type': "HOT Worked (d/h)",
            # 'work_day_days': round(HOT_day,2),
            'work_day_days': round(HOT_Hour / standard_work_hour, 2),
            'work_day_hour': round(HOT_Hour, 2),
            'work_day_formula': 'from timesheet : worked in weekend (d/h) + worked in public working (d/h)'

        }

        if not_hour>0 and absent_hour==0:
            result['8'] = {
                'work_day_id': self.id,
                'work_day_type': "NOT Worked (d/h)",
                'work_day_days': round(not_day, 2),
                'work_day_hour': round(not_hour, 2),
                'work_day_formula': 'net worked(d/h) - net working(d/h)'

            }
        elif not_hour>0 and absent_hour>0:
            result['8'] = {
                'work_day_id': self.id,
                'work_day_type': "NOT Worked (d/h)",
                'work_day_days': round(not_day, 2),
                'work_day_hour': round(not_hour, 2),
                'work_day_formula': 'net worked(d/h) - net working(d/h)'

            }
            if leave_with_pay_hour > 0:
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day - leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h)'

                }
                result['10'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Pay",
                    'work_day_days': round(leave_with_pay, 2),
                    'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            # elif leave_with_out_pay_dates:
            elif leave_with_out_pay_hour > 0:
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day- leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }
                result['10'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Out Pay",
                    'work_day_days': round(leave_with_out_pay, 2),
                    'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            # elif leave_with_pay_dates and leave_with_out_pay_dates:
            elif leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day - leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }
                result['10'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Pay",
                    'work_day_days': round(leave_with_pay, 2),
                    'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
                result['11'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Out Pay",
                    'work_day_days': round(leave_with_out_pay, 2),
                    'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            else:
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day, 2),
                    'work_day_hour': round(absent_hour, 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }

        if not_hour==0 and absent_hour>0:
            if leave_with_pay_hour > 0:
                result['8'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day - leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h)'

                }
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Pay",
                    'work_day_days': round(leave_with_pay, 2),
                    'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            # elif leave_with_out_pay_dates:
            elif leave_with_out_pay_hour > 0:
                result['8'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day- leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Out Pay",
                    'work_day_days': round(leave_with_out_pay, 2),
                    'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            # elif leave_with_pay_dates and leave_with_out_pay_dates:
            elif leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                result['8'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day - leave_with_pay - leave_with_out_pay, 2),
                    'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                leave_with_out_pay * standard_work_hour), 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }
                result['9'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Pay",
                    'work_day_days': round(leave_with_pay, 2),
                    'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
                result['10'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Leave With Out Pay",
                    'work_day_days': round(leave_with_out_pay, 2),
                    'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                    'work_day_formula': 'from timesheet'

                }
            else:
                result['8'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Absent",
                    'work_day_days': round(absent_day, 2),
                    'work_day_hour': round(absent_hour, 2),
                    'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                }


        # if not_hour < 0:
        #     # if leave_with_pay_dates:
        #     if leave_with_pay_hour > 0:
        #         result['8'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Absent",
        #             'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
        #             'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
        #                         leave_with_out_pay * standard_work_hour), 2),
        #             'work_day_formula': 'net worked(d/h) - net working(d/h)'
        #
        #         }
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Pay",
        #             'work_day_days': round(leave_with_pay, 2),
        #             'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #     # elif leave_with_out_pay_dates:
        #     elif leave_with_out_pay_hour > 0:
        #         result['8'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Absent",
        #             'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
        #             'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
        #                         leave_with_out_pay * standard_work_hour), 2),
        #             'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'
        #
        #         }
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Out Pay",
        #             'work_day_days': round(leave_with_out_pay, 2),
        #             'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #     # elif leave_with_pay_dates and leave_with_out_pay_dates:
        #     elif leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
        #         result['8'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Absent",
        #             'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
        #             'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
        #                         leave_with_out_pay * standard_work_hour), 2),
        #             'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'
        #
        #         }
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Pay",
        #             'work_day_days': round(leave_with_pay, 2),
        #             'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #         result['10'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Out Pay",
        #             'work_day_days': round(leave_with_out_pay, 2),
        #             'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #
        #
        #     else:
        #         result['8'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Absent",
        #             'work_day_days': round((-1) * not_day, 2),
        #             'work_day_hour': round((-1) * not_hour, 2),
        #             'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'
        #
        #         }
        #
        #
        # else:
        #
        #     result['8'] = {
        #         'work_day_id': self.id,
        #         'work_day_type': "NOT Worked (d/h)",
        #         'work_day_days': round(not_day, 2),
        #         'work_day_hour': round(not_hour, 2),
        #         'work_day_formula': 'net worked(d/h) - net working(d/h)'
        #
        #     }
        #     if leave_with_pay_hour > 0:
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Pay",
        #             'work_day_days': round(leave_with_pay, 2),
        #             'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #     elif leave_with_out_pay_hour > 0:
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Out Pay",
        #             'work_day_days': round(leave_with_out_pay, 2),
        #             'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #     elif leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
        #         result['9'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Pay",
        #             'work_day_days': round(leave_with_pay, 2),
        #             'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }
        #         result['10'] = {
        #             'work_day_id': self.id,
        #             'work_day_type': "Leave With Out Pay",
        #             'work_day_days': round(leave_with_out_pay, 2),
        #             'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
        #             'work_day_formula': 'from timesheet'
        #
        #         }

        return result.values()

    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
        standard_work_hour = self.struct_id.standard_working_hour
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }


        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                hours = 0
                rate_per_hours = 0
                ot_rate = 1.00
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                if rule.code.upper().startswith('NOTSAL') and tot_rule<0:
                    tot_rule=0
                if rule.code.upper().startswith('ABSENT') and tot_rule>0:
                    tot_rule=0

                if rule.code.upper().startswith('LWOP'):
                    rate_per_hours=(self.contract_id.wage+self.contract_id.food_allowance+self.contract_id.vehicle_allowance+self.contract_id.telephone_allowance+self.contract_id.other_allowance)*12/365/standard_work_hour
                    ot_rate=1
                    hours=self.employee_id.get_leave_with_out_pay(self.employee_id.id,self.date_from,self.date_to)

                    amount = hours * rate_per_hours * ot_rate
                    tot_rule=amount

                if rule.code.upper().startswith('ABSENT'):
                    # leave_without_pay_hours = self.employee_id.get_leave_with_out_pay(self.employee_id.id, self.date_from, self.date_to)
                    rate_per_hours=self.contract_id.wage*12/365/standard_work_hour
                    ot_rate=1
                    hours=self.employee_id.get_absent_time(self.employee_id.id,self.date_from,self.date_to)
                    amount = hours * rate_per_hours * ot_rate
                    # if hours>0:
                    #     amount=0
                    tot_rule=amount


                if rule.code.upper().startswith('LWP'):
                    rate_per_hours=(self.contract_id.wage+self.contract_id.food_allowance+self.contract_id.vehicle_allowance+self.contract_id.telephone_allowance+self.contract_id.other_allowance)*12/365/standard_work_hour
                    ot_rate=1
                    hours=self.employee_id.get_leave_with_pay(self.employee_id.id,self.date_from,self.date_to)
                    amount = hours * rate_per_hours * ot_rate
                    tot_rule=amount


                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results

                if rule.code.upper().startswith('R1HPOB'):
                    if self.sum_worked_hours>0:
                        hours=self.sum_worked_hours
                        rate_per_hours=self.contract_id.wage/hours
                if rule.code.upper().startswith('BASIC'):
                    monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                         ('date', '<=', self.date_to)]).mapped('unit_amount'))

                    if monthly_total_work_hour>0:
                        hours=monthly_total_work_hour
                        rate_per_hours=round(self.contract_id.wage/hours,2)

                if rule.code.upper().startswith('HPTS1001'):
                    monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                        [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                         ('date', '<=', self.date_to)]).mapped('unit_amount'))
                    if monthly_total_work_hour>0:
                        hours=monthly_total_work_hour
                        rate_per_hours=round(self.contract_id.hourly_wage,2)

                if rule.code.upper().startswith('NOTSAL'):
                    # rate_per_hours=self.contract_id.wage*12/365/standard_work_hour
                    rate_per_hours=self.struct_id.not_rate
                    ot_rate=1
                    hours=self.employee_id.get_not_overtime(self.employee_id.id,self.date_from,self.date_to)


                if rule.code.upper().startswith('HOTSAL'):
                    # rate_per_hours = self.contract_id.wage * 12 / 365 / standard_work_hour
                    rate_per_hours = self.struct_id.hot_rate
                    ot_rate = 1
                    hours = self.employee_id.get_hot_overtime(self.employee_id.id, self.date_from, self.date_to)
                # if rule.code.upper().startswith('NOTSAL'):
                #     if amount>=0:
                #         result[rule.code] = {
                #             'sequence': rule.sequence,
                #             'code': rule.code,
                #             'name': rule.name,
                #             'note': rule.note,
                #             'salary_rule_id': rule.id,
                #             'contract_id': contract.id,
                #             'employee_id': employee.id,
                #             'amount': amount,
                #             'hours': hours,
                #             'rate_per_hours': rate_per_hours,
                #             'ot_rate': ot_rate,
                #             'quantity': qty,
                #             'rate': rate,
                #             'slip_id': self.id,
                #         }
                # elif rule.code.upper().startswith('ABSENT'):
                #     if amount<0:
                #         result[rule.code] = {
                #             'sequence': rule.sequence,
                #             'code': rule.code,
                #             'name': rule.name,
                #             'note': rule.note,
                #             'salary_rule_id': rule.id,
                #             'contract_id': contract.id,
                #             'employee_id': employee.id,
                #             'amount':(-1)* amount,
                #             'hours':(-1)* hours,
                #             'rate_per_hours': rate_per_hours,
                #             'ot_rate': ot_rate,
                #             'quantity': qty,
                #             'rate': rate,
                #             'slip_id': self.id,
                #         }
                    # else:
                    #     result[rule.code] = {
                    #         'sequence': rule.sequence,
                    #         'code': rule.code,
                    #         'name': rule.name,
                    #         'note': rule.note,
                    #         'salary_rule_id': rule.id,
                    #         'contract_id': contract.id,
                    #         'employee_id': employee.id,
                    #         'amount': amount,
                    #         'hours': hours,
                    #         'rate_per_hours': rate_per_hours,
                    #         'ot_rate': ot_rate,
                    #         'quantity': qty,
                    #         'rate': rate,
                    #         'slip_id': self.id,
                    #     }

                if rule.code.upper().startswith('LWP'):
                    if amount!=0:
                        result[rule.code] = {
                            'sequence': rule.sequence,
                            'code': rule.code,
                            'name': rule.name,
                            'note': rule.note,
                            'salary_rule_id': rule.id,
                            'contract_id': contract.id,
                            'employee_id': employee.id,
                            'amount':amount,
                            'hours':hours,
                            'rate_per_hours': rate_per_hours,
                            'ot_rate': ot_rate,
                            'quantity': qty,
                            'rate': rate,
                            'slip_id': self.id,
                        }
                elif rule.code.upper().startswith('LWOP'):
                    if amount!=0:
                        result[rule.code] = {
                            'sequence': rule.sequence,
                            'code': rule.code,
                            'name': rule.name,
                            'note': rule.note,
                            'salary_rule_id': rule.id,
                            'contract_id': contract.id,
                            'employee_id': employee.id,
                            'amount':amount,
                            'hours':hours,
                            'rate_per_hours': rate_per_hours,
                            'ot_rate': ot_rate,
                            'quantity': qty,
                            'rate': rate,
                            'slip_id': self.id,
                        }

                else:
                    result[rule.code] = {
                        'sequence': rule.sequence,
                        'code': rule.code,
                        'name': rule.name,
                        'note': rule.note,
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'employee_id': employee.id,
                        'amount': amount,
                        'hours':hours,
                        'rate_per_hours':rate_per_hours,
                        'ot_rate':ot_rate,
                        'quantity': qty,
                        'rate': rate,
                        'slip_id': self.id,
                    }
        return result.values()