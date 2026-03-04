import calendar

from odoo import models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # def get_not_overtime(self, id, start_date, end_date):
    #     over_time_rec = self.env['hr.overtime.line'].search(
    #         [('employee_id', '=', self.id), ('date', '>=', start_date),
    #          ('date', '<=', end_date), ('ot_type', '=', 'not'), ('state', '=', 'approved')])
    #     total = 0.0
    #     for line in over_time_rec:
    #         total = total + line.number_of_hours
    #
    #     return total
    #
    # def get_hot_overtime(self, id, start_date, end_date):
    #     over_time_rec = self.env['hr.overtime.line'].search(
    #         [('employee_id', '=', self.id), ('date', '>=', start_date),
    #          ('date', '<=', end_date), ('ot_type', '=', 'hot'), ('state', '=', 'approved')])
    #     total = 0.0
    #     for line in over_time_rec:
    #         total = total + line.number_of_hours
    #
    #     return total

    def get_not_overtime(self, id, start_date, end_date):
        not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        return not_hour

    def get_hot_overtime(self, id, start_date, end_date):
        not_hour,hot_hour=self.employee_monthly_work_history(id, start_date, end_date)
        return hot_hour

    def employee_monthly_work_history(self,id,start_date, end_date):
        standard_work_hour = self.contract_id.structure_type_id.default_struct_id.standard_working_hour
        c = calendar.Calendar()

        year = start_date.year
        month = start_date.month
        calendar_day = calendar.monthrange(year, month)
        calendar_days = calendar_day[1]

        weekend = self.contract_id.structure_type_id.default_struct_id.weekend_day
        monthcal = c.monthdatescalendar(year, month)
        weekend_day = []
        weekend_day.append(calendar.SUNDAY)
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

        monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
            [('employee_id', '=', id), ('date', '>=', start_date),
             ('date', '<=', end_date)]).mapped('unit_amount'))

        #######PUBLIC HOLIDAY###########
        ph_day = 0
        public_holidays = self.env['hr.leave'].sudo().search(
            [('mode_company_id', '=', self.company_id.id),
             ('date_from', '>=', start_date), ('date_to', '<=', end_date)], order='date_from')

        for holiday in public_holidays:
            ph_day += holiday.number_of_days
        #######PUBLIC HOLIDAY###########

        net_working_day = calendar_days - number_of_weekday
        net_working_hour = round(calendar_days * standard_work_hour - number_of_weekday * standard_work_hour, 2)
        HOT_day = ph_day
        HOT_Hour = round(ph_day * standard_work_hour, 2)
        monthly_total_day = monthly_total_work_hour / standard_work_hour
        monthly_total_hour = round(monthly_total_work_hour, 2)
        net_worked_day = monthly_total_day - HOT_day
        net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)

        not_day = net_working_day - net_worked_day
        not_hour =  net_worked_hour-net_working_hour

        return not_hour,HOT_Hour
