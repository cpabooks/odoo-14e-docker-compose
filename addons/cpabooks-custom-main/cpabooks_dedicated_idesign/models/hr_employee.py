import calendar
import datetime

from dateutil.relativedelta import relativedelta

from odoo import models,fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def employee_monthly_work_history(self,id,start_date, end_date):
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

        weekday_dates = [day for week in monthcal for day in week if \
                         day.weekday() in weekend_day and \
                         day.month == month]

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
                 ('date', '<=', end_date),('date','not in',weekday_dates)])
            monthly_total_work_hour = 0
            monthly_not_hour = 0
            for time in work_days_time:
                if time.unit_amount <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                    monthly_total_work_hour += time.unit_amount
                else:
                    monthly_not_hour += time.unit_amount - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                    monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

            monthly_actual_timesheet_hour = sum(self.env['account.analytic.line'].sudo().search(
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
        # query = """select * from hr_leave  where date_part('month','{}'::date)={} and date_part('year','{}'::date)={} and type_for='{}'""".format(
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
        net_working_hour = round(calendar_days * standard_work_hour - number_of_weekday * standard_work_hour-ph_day*standard_work_hour, 2)
        # HOT_Hour = round(ph_day * standard_work_hour, 2)
        HOT_Hour = round(public_holiday_work_hour, 2)-round(work_hour_need_to_remove,2)

        net_worked_hour = round(monthly_total_work_hour, 2)
        not_hour = round(monthly_not_hour, 2)

        absent_hour = round(net_working_hour - net_worked_hour, 2)

        return absent_hour,not_hour,HOT_Hour

    def get_not_overtime(self, id, start_date, end_date):
        absent_hour,not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        return not_hour
    def get_hot_overtime(self, id, start_date, end_date):
        absent_hour,not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        return hot_hour

    def get_absent_time(self, id, start_date, end_date):
        absent_hour,not_hour, hot_hour = self.employee_monthly_work_history(id, start_date, end_date)
        return absent_hour