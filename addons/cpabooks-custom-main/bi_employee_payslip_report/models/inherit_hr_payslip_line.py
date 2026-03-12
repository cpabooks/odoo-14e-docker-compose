import calendar
import datetime

from dateutil.relativedelta import relativedelta
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, Payslips, WorkedDays, InputLine
from odoo import models, fields, api,_
from odoo.tools import format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    hourly_rate_line_ids = fields.One2many('hr.payslip.hourly.line', 'hour_id', compute='_compute_line_ids', store=True,
                               string='Hourly Payslip Lines', readonly=True,
                               states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    custom_working_days_inputs = fields.One2many('working.days.inputs', 'work_day_id', compute='_compute_line_ids', store=True,
                                            string='Working Days & Inputs', readonly=True,
                                            states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    # working_hour_calc_ids = fields.One2many('working.hours.calc', 'payslip_id', compute='_compute_line_ids', store=True,
    #                            string='Working Hour Calc.', readonly=True,
    #                            states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})

    salary_package = fields.One2many('employee.salary.package', 'payslip_id',
                                                 store=True,
                                                 states={'draft': [('readonly', False)],
                                                         'verify': [('readonly', False)]})

    deduction_amount=fields.Float(string="Deduction Amount")
    extra_amount=fields.Float(string="Extra Effort Amount")

    def action_payslip_done(self):
        for payslip in self:
            hr_payslip = self.env['hr.payslip'].search(
                [('employee_id', '=', payslip.employee_id.id), ('date_from', '>=', payslip.date_from),
                 ('date_to', '<=', payslip.date_to), ('state', '=', 'done')])
            if hr_payslip:
                raise UserError(("%s has done payslip on same period" % self.employee_id.name))
        return super(HrPayslip, self).action_payslip_done()

    def action_payslip_cancel(self):
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()


    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()
        for rec in self:
            rec.move_id.post()
        return res

    def action_payslip_cancel(self):
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_draft()
        moves.posted_before=False
        return super(InheritHRPayslip, self).action_payslip_cancel()


    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state in ['draft', 'verify']):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            payslip.hourly_rate_line_ids.unlink()
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            hourly_lines=[(0, 0, line) for line in payslip._get_hourly_payslip_lines()]
            # working_hour_calc_lines=[(0, 0, line) for line in payslip._get_working_hour_calc()]
            if str('Timesheet').upper() in payslip.struct_id.name.upper():
                payslip.custom_working_days_inputs=[(5,0,0)]
                custom_working_days_inputs=[]
            else:
                custom_working_days_inputs = [(0, 0, line) for line in payslip._get_custom_working_days_inputs()]
            if payslip.contract_id.wage_type=='monthly':
                salary_package_computation=[(0, 0, line) for line in payslip._get_salary_package()]
                payslip.write({'line_ids': lines, 'hourly_rate_line_ids': hourly_lines,
                               'custom_working_days_inputs': custom_working_days_inputs,'salary_package':salary_package_computation, 'number': number,
                               'state': 'verify', 'compute_date': fields.Date.today()})
            else:
                payslip.write({'line_ids': lines,'hourly_rate_line_ids':hourly_lines,'custom_working_days_inputs':custom_working_days_inputs, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True

    def _get_salary_package(self):
        self.salary_package=[(5,0,0)]
        result = {}
        result['1'] = {
            'payslip_id': self.id,
            'type': "Basic Salary",
            'amount': self.contract_id.wage
        }
        result['2'] = {
            'payslip_id': self.id,
            'type': "Food Allowance",
            'amount': self.contract_id.food_allowance
        }
        result['3'] = {
            'payslip_id': self.id,
            'type': "Other Allowance",
            'amount': self.contract_id.other_allowance
        }
        result['4'] = {
            'payslip_id': self.id,
            'type': "Telephone Allowance",
            'amount': self.contract_id.telephone_allowance
        }
        result['5'] = {
            'payslip_id': self.id,
            'type': "Vehicle Allowance",
            'amount': self.contract_id.vehicle_allowance
        }
        return result.values()

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            hours_per_day = self._get_worked_day_lines_hours_per_day()
            work_hours = contract._get_work_hours(self.date_from, self.date_to, domain=domain)
            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
            add_days_rounding = 0
            for work_entry_type_id, hours in work_hours_ordered:
                calendar_days=0
                calendar_hours=0
                weekend_days=0
                weekend_hours=0
                public_holidays=0
                public_holidays_hour=0

                work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
                days = round(hours / hours_per_day, 5) if hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)

                if work_entry_type_id!=1:
                    year = self.date_from.year
                    month = self.date_from.month

                    ###################################region Weekend day calculation########################################
                    calendar_day = calendar.monthrange(year, month)
                    calendar_days=calendar_day[1]
                    calendar_hours = calendar_days * hours_per_day
                    weekend_days =calendar_days-day_rounded
                    weekend_hours = weekend_days * hours_per_day
                    ###################################endregion weekend day calculation########################################
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'calendar_days':calendar_days,
                    'calendar_hours':calendar_hours,
                    'weekend_days':weekend_days,
                    'weekend_hours':weekend_hours,
                    'public_holidays':public_holidays,
                    'public_holidays_hours':public_holidays_hour,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                }
                res.append(attendance_line)

            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_contract_calendar()
            if self.date_from < contract.date_start :
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                out_days += out_time['days']
                out_hours += out_time['hours']
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                out_days += out_time['days']
                out_hours += out_time['hours']

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res

    def _get_payslip_lines(self):
        if self.struct_id.overtime_cal_method=='on_monthly':
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
                        rate_per_hours=(self.contract_id.wage+self.contract_id.food_allowance+self.contract_id.vehicle_allowance+self.contract_id.telephone_allowance+self.contract_id.other_allowance)*12/365/standard_work_hour
                        ot_rate=1
                        hours=self.employee_id.get_not_overtime(self.employee_id.id,self.date_from,self.date_to)
                        amount = hours * rate_per_hours * ot_rate
                        if hours>0:
                            amount=0
                        tot_rule=(-1)*amount


                    if rule.code.upper().startswith('LWP'):
                        rate_per_hours=(self.contract_id.wage+self.contract_id.food_allowance+self.contract_id.vehicle_allowance+self.contract_id.telephone_allowance+self.contract_id.other_allowance)*12/365/standard_work_hour
                        ot_rate=1
                        hours=self.employee_id.get_leave_with_pay(self.employee_id.id,self.date_from,self.date_to)
                        amount = hours * rate_per_hours * ot_rate
                        tot_rule=amount

                    if rule.code.upper().startswith('HPOT'):
                        monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                             ('date', '<=', self.date_to)]).mapped('unit_amount'))
                        if monthly_total_work_hour>0:
                            hours=monthly_total_work_hour
                            rate_per_hours=round(self.contract_id.hourly_wage,2)
                            amount=hours*rate_per_hours
                            tot_rule=amount
                        else:
                            hours = 0
                            rate_per_hours = round(self.contract_id.hourly_wage, 2)
                            amount = 0
                            tot_rule = amount
                    # if rule.code.upper().startswith('BASIC') and self.contract_id.wage_type=='hourly':
                    #     monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                    #         [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                    #          ('date', '<=', self.date_to)]).mapped('unit_amount'))
                    #
                    #     if monthly_total_work_hour>0:
                    #         rate_per_hours = round(self.contract_id.hourly_wage, 2)
                    #         amount = monthly_total_work_hour * rate_per_hours
                    #         tot_rule = amount


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
                            # if self.contract_id.wage_type=='hourly':
                            #     rate_per_hours = round(self.contract_id.hourly_wage, 2)
                            # else:
                            rate_per_hours=round(self.contract_id.wage/hours,2)

                    if rule.code.upper().startswith('HPTS1001'):
                        monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                             ('date', '<=', self.date_to)]).mapped('unit_amount'))
                        if monthly_total_work_hour>0:
                            hours=monthly_total_work_hour
                            rate_per_hours=round(self.contract_id.hourly_wage,2)

                    # if rule.code.upper().startswith('HPOT'):
                    #     monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                    #         [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                    #          ('date', '<=', self.date_to)]).mapped('unit_amount'))
                    #     if monthly_total_work_hour>0:
                    #         hours=monthly_total_work_hour
                    #         rate_per_hours=round(self.contract_id.hourly_wage,2)
                    #         amount=hours*rate_per_hours
                    #         localdict[rule.code]=amount

                    if rule.code.upper().startswith('NOTSAL'):
                        # rate_per_hours=self.contract_id.wage*12/365/standard_work_hour
                        # ot_rate=self.struct_id.not_rate

                        rate_per_hours = self.struct_id.not_rate
                        if self.contract_id.not_rate>0 and self.contract_id.not_rate!=self.struct_id.not_rate:
                            rate_per_hours = self.contract_id.not_rate
                        ot_rate = 1
                        hours=self.employee_id.get_not_overtime(self.employee_id.id,self.date_from,self.date_to)


                    if rule.code.upper().startswith('HOTSAL'):
                        # rate_per_hours = self.contract_id.wage * 12 / 365 / standard_work_hour
                        # ot_rate = self.struct_id.hot_rate
                        # rate_per_hours = self.struct_id.hot_rate
                        rate_per_hours = self.struct_id.hot_rate
                        if self.contract_id.hot_rate > 0 and self.contract_id.hot_rate != self.struct_id.hot_rate:
                            rate_per_hours = self.contract_id.hot_rate
                        ot_rate = 1
                        hours = self.employee_id.get_hot_overtime(self.employee_id.id, self.date_from, self.date_to)
                    if rule.code.upper().startswith('NOTSAL'):
                        if amount>=0:
                            result[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'amount': amount,
                                'hours': hours,
                                'rate_per_hours': rate_per_hours,
                                'ot_rate': ot_rate,
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': self.id,
                            }
                    elif rule.code.upper().startswith('ABSENT'):
                        if amount<0:
                            result[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'amount':(-1)* amount,
                                'hours':(-1)* hours,
                                'rate_per_hours': rate_per_hours,
                                'ot_rate': ot_rate,
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': self.id,
                            }
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

                    elif rule.code.upper().startswith('LWP'):
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
        else:
            def _sum_salary_rule_category(localdict, category, amount):
                if category.parent_id:
                    localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
                localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code,
                                                                                               0) + amount
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
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    if rule.code.upper().startswith('NOTSAL') and tot_rule < 0:
                        tot_rule = 0
                    if rule.code.upper().startswith('ABSENT') and tot_rule > 0:
                        tot_rule = 0

                    if rule.code.upper().startswith('LWOP'):
                        rate_per_hours = (
                                                     self.contract_id.wage + self.contract_id.food_allowance + self.contract_id.vehicle_allowance + self.contract_id.telephone_allowance + self.contract_id.other_allowance) * 12 / 365 / standard_work_hour
                        ot_rate = 1
                        hours = self.employee_id.get_leave_with_out_pay(self.employee_id.id, self.date_from,
                                                                        self.date_to)

                        amount = hours * rate_per_hours * ot_rate
                        tot_rule = amount

                    if rule.code.upper().startswith('ABSENT'):
                        # leave_without_pay_hours = self.employee_id.get_leave_with_out_pay(self.employee_id.id, self.date_from, self.date_to)
                        # rate_per_hours = self.contract_id.wage * 12 / 365 / standard_work_hour
                        rate_per_hours=(self.contract_id.wage+self.contract_id.food_allowance+self.contract_id.vehicle_allowance+self.contract_id.telephone_allowance+self.contract_id.other_allowance)*12/365/standard_work_hour
                        ot_rate = 1
                        hours = self.employee_id.get_absent_time(self.employee_id.id, self.date_from, self.date_to)
                        amount = hours * rate_per_hours * ot_rate
                        # if hours>0:
                        #     amount=0
                        tot_rule = amount

                    if rule.code.upper().startswith('LWP'):
                        rate_per_hours = (
                                                     self.contract_id.wage + self.contract_id.food_allowance + self.contract_id.vehicle_allowance + self.contract_id.telephone_allowance + self.contract_id.other_allowance) * 12 / 365 / standard_work_hour
                        ot_rate = 1
                        hours = self.employee_id.get_leave_with_pay(self.employee_id.id, self.date_from, self.date_to)
                        amount = hours * rate_per_hours * ot_rate
                        tot_rule = amount

                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results

                    if rule.code.upper().startswith('R1HPOB'):
                        if self.sum_worked_hours > 0:
                            hours = self.sum_worked_hours
                            rate_per_hours = self.contract_id.wage / hours
                    if rule.code.upper().startswith('BASIC'):
                        monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                             ('date', '<=', self.date_to)]).mapped('unit_amount'))

                        if monthly_total_work_hour > 0:
                            hours = monthly_total_work_hour
                            rate_per_hours = round(self.contract_id.wage / hours, 2)

                    if rule.code.upper().startswith('HPTS1001'):
                        monthly_total_work_hour = sum(self.env['account.analytic.line'].sudo().search(
                            [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                             ('date', '<=', self.date_to)]).mapped('unit_amount'))
                        if monthly_total_work_hour > 0:
                            hours = monthly_total_work_hour
                            rate_per_hours = round(self.contract_id.hourly_wage, 2)

                    if rule.code.upper().startswith('NOTSAL'):
                        # rate_per_hours=self.contract_id.wage*12/365/standard_work_hour
                        # rate_per_hours = self.struct_id.not_rate
                        rate_per_hours = self.struct_id.not_rate
                        if self.contract_id.not_rate > 0 and self.contract_id.not_rate != self.struct_id.not_rate:
                            rate_per_hours = self.contract_id.not_rate
                        ot_rate = 1
                        hours = self.employee_id.get_not_overtime(self.employee_id.id, self.date_from, self.date_to)

                    if rule.code.upper().startswith('HOTSAL'):
                        # rate_per_hours = self.contract_id.wage * 12 / 365 / standard_work_hour
                        # rate_per_hours = self.struct_id.hot_rate
                        rate_per_hours = self.struct_id.hot_rate
                        if self.contract_id.hot_rate > 0 and self.contract_id.hot_rate != self.struct_id.hot_rate:
                            rate_per_hours = self.contract_id.hot_rate
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
                        if amount != 0:
                            result[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'amount': amount,
                                'hours': hours,
                                'rate_per_hours': rate_per_hours,
                                'ot_rate': ot_rate,
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': self.id,
                            }
                    elif rule.code.upper().startswith('LWOP'):
                        if amount != 0:
                            result[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'amount': amount,
                                'hours': hours,
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
                            'hours': hours,
                            'rate_per_hours': rate_per_hours,
                            'ot_rate': ot_rate,
                            'quantity': qty,
                            'rate': rate,
                            'slip_id': self.id,
                        }
        return result.values()

    def _get_hourly_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
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
        # for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
        for rule in self.env['hr.salary.rule'].search([('code','=','HPOT')],limit=1):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                # amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict

                query="""select sum(unit_amount) from account_analytic_line  where date::Date>='{}' 
                and date::Date<='{}' and employee_id={} and company_id={}""".format(self.date_from,self.date_to,employee.id,employee.company_id.id)
                self._cr.execute(query=query)
                timesheet_total_hour=self._cr.fetchall()

                qty = timesheet_total_hour[0][0] if timesheet_total_hour[0][0]!=None else 0
                rate = contract.salary_per_h
                tot_rule=qty*rate
                amount=qty*rate
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'hour': qty,
                    'hour_rate': rate,
                    'hour_id': self.id,
                }
        return result.values()

    def _get_custom_working_days_inputs(self):
        number_of_half_day,actual_half_day_need_to_work,get_work_duration_half_days,get_pay_hour=self.employee_id.get_half_day_details(self.employee_id.id,self.date_from,self.date_to)
        half_day_consider_hour=actual_half_day_need_to_work-get_work_duration_half_days
        if self.struct_id.overtime_cal_method=='on_monthly':
            self.custom_working_days_inputs = [(5, 0, 0)]
            # fill only if the contract as a working schedule linked
            self.ensure_one()







            standard_work_hour = self.struct_id.standard_working_hour
            c = calendar.Calendar()

            year = self.date_from.year
            month = self.date_from.month
            calendar_day = calendar.monthrange(year, month)
            calendar_days = calendar_day[1]
            weekend=self.env['week.day']
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




            if self.struct_id.structure_type=='basic_pay_office_stuff':
                monthly_total_work_hour = sum(self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                     ('date_start', '<=', self.date_to)]).mapped('duration'))
                count_day_monthly_total_work_hour=self.env['hr.work.entry'].sudo().search_count(
                    [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                     ('date_start', '<=', self.date_to)])

            else:
                monthly_total_work_hour=sum(self.env['account.analytic.line'].sudo().search([('employee_id','=',self.employee_id.id),('date','>=',self.date_from),('date','<=',self.date_to)]).mapped('unit_amount'))
                count_day_monthly_total_work_hour=self.env['account.analytic.line'].sudo().search_count([('employee_id','=',self.employee_id.id),('date','>=',self.date_from),('date','<=',self.date_to)])
            #######PUBLIC HOLIDAY###########
            ph_day=0
            public_holidays=self.env['hr.leave'].sudo().search([('mode_company_id','=',self.contract_id.employee_id.company_id.id),
                                                                     ('date_from','>=',self.date_from),('date_to','<=',self.date_to)],order='date_from')



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
            weekend_work_hour=0
            public_holiday_only=0
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
            public_holiday_dates=[]

            for holiday in public_holidays:
                #need to remove weekend date from here
                from_date=holiday.date_from+datetime.timedelta(hours=6)
                to_date=holiday.date_to+datetime.timedelta(hours=6)
                delta=to_date.date()-from_date.date()
                for i in range(delta.days + 1):
                    day = from_date + datetime.timedelta(days=i)
                    public_holiday_dates.append(day.date())

                public_holiday_work_hour += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))
                public_holiday_only += sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date', '>=', from_date),
                     ('date', '<=', to_date)]).mapped('unit_amount'))


                ph_day+=holiday.number_of_days
            date_need_to_remove_from_holiday = 0
            work_hour_need_to_remove=0
            if len(public_holiday_dates)>0:
                for weekend_date in weekend_date_this_month:
                    if weekend_date in public_holiday_dates:
                        date_need_to_remove_from_holiday+=1
                        work_hour_need_to_remove+=sum(self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date', '=', weekend_date)]).mapped('unit_amount'))
                ph_day-=date_need_to_remove_from_holiday

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
            leave_with_pay_hour=self.employee_id.get_leave_with_pay(self.employee_id.id,self.date_from,self.date_to)
            leave_with_pay=leave_with_pay_hour/standard_work_hour
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
            leave_with_out_pay_hour = self.employee_id.get_leave_with_out_pay(self.employee_id.id,self.date_from,self.date_to)
            leave_with_out_pay=leave_with_out_pay_hour/standard_work_hour



            #######Leave With Out Pay###########
            number_of_half_day, actual_half_day_need_to_work, get_work_duration_half_days, get_pay_hour=self.employee_id.get_half_day_details(self.employee_id.id,self.date_from,self.date_to)

            net_working_day=calendar_days-number_of_weekday - ph_day
            net_working_hour=round(calendar_days*standard_work_hour- number_of_weekday * standard_work_hour-ph_day*standard_work_hour,2)

            HOT_day = ph_day
            # HOT_Hour = round(ph_day * standard_work_hour, 2)
            HOT_Hour = round(public_holiday_work_hour, 2)-round(work_hour_need_to_remove,2)
            monthly_total_day = monthly_total_work_hour / standard_work_hour
            monthly_total_hour = round(monthly_total_work_hour, 2)
            net_worked_day = monthly_total_day - HOT_day
            net_worked_hour=round(monthly_total_hour-HOT_Hour,2)

            actual_need_to_work=net_working_hour
            but_emp_work=monthly_total_work_hour-HOT_Hour
            extra_time_work=0
            # if but_emp_work>actual_need_to_work:
            extra_time_work=but_emp_work-actual_need_to_work
            # not_day=net_worked_day-net_working_day
            # not_hour=net_worked_hour-net_working_hour

            not_hour=extra_time_work
            not_day=extra_time_work/standard_work_hour
            # not_hour=weekend_work_hour
            # not_day=not_hour/8
            result = {}
            result['1'] = {
                'work_day_id': self.id,
                'work_day_type': "Calendar Working",
                'work_day_days': round(float(calendar_days),2),
                'work_day_hour': round(calendar_days*standard_work_hour,2),
                'work_day_formula':'total calendar days x {} hrs'.format(standard_work_hour)

            }
            result['2'] = {
                'work_day_id': self.id,
                'work_day_type': "Weekend",
                'work_day_days': round(float(number_of_weekday),2),
                'work_day_hour': round(number_of_weekday * standard_work_hour,2),
                'work_day_formula': 'number of weekend days x {} hrs'.format(standard_work_hour)

            }
            result['3'] = {
                'work_day_id': self.id,
                'work_day_type': "Holiday",
                'work_day_days': round(float(HOT_day), 2),
                # 'work_day_hour': round(public_holiday_only, 2),
                'work_day_hour': round(HOT_day*standard_work_hour, 2),
                'work_day_formula': 'number of holiday days x {} hrs'.format(standard_work_hour)

            }
            result['4'] = {
                'work_day_id': self.id,
                'work_day_type': "Net Working (d/h)",
                'work_day_days': round(float(net_working_day),2),
                'work_day_hour': round(net_working_hour,2),
                'work_day_formula': 'calendar working (d/h) - weekend (d/h) - public working (d/h)'

            }

            result['5'] = {
                'work_day_id': self.id,
                'work_day_type': "Net Worked (d/h)",
                'work_day_days': round(net_worked_day,2),
                'work_day_hour': round(net_worked_hour,2),
                'work_day_formula': 'acutal ts duration (d/h) - weekend (d/h) - public working (d/h)'

            }
            if self.struct_id.structure_type == 'basic_pay_office_stuff':
                result['6'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Actual WE Duration (d/h)",
                    'work_day_days': round(monthly_total_day,2),
                    'work_day_hour': round(monthly_total_hour,2),
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
                'work_day_days': round(HOT_Hour/standard_work_hour,2),
                'work_day_hour': round(HOT_Hour,2),
                'work_day_formula': 'from timesheet : worked in weekend (d/h) + worked in public working (d/h)'

            }

            if self.struct_id.structure_type == 'basic_pay_office_stuff':
                if not_hour<0:
                    # if leave_with_pay_dates:
                    if leave_with_pay_hour>0 and leave_with_out_pay_hour>0:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day)-leave_with_pay-leave_with_out_pay-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(((-1) * not_hour)-(leave_with_pay*standard_work_hour)-(leave_with_out_pay*standard_work_hour)-half_day_consider_hour, 2),
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
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    elif leave_with_pay_hour>0:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day)-leave_with_pay-leave_with_out_pay-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(((-1) * not_hour)-(leave_with_pay*standard_work_hour)-(leave_with_out_pay*standard_work_hour)-half_day_consider_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h)'

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
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    # elif leave_with_out_pay_dates:
                    elif leave_with_out_pay_hour>0:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day)-leave_with_pay-leave_with_out_pay-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(((-1) * not_hour)-(leave_with_pay*standard_work_hour)-(leave_with_out_pay*standard_work_hour)-half_day_consider_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    # elif leave_with_pay_dates and leave_with_out_pay_dates:



                    else:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day)-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round((-1) * not_hour-half_day_consider_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }


                else:

                    result['8'] = {
                        'work_day_id': self.id,
                        'work_day_type': "NOT Worked (d/h)",
                        'work_day_days': round(not_day,2),
                        'work_day_hour': round(not_hour,2),
                        'work_day_formula': 'net worked(d/h) - net working(d/h)'

                    }
                    if leave_with_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    if leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
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
                if not_hour < 0:
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
                            'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
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
                    # if leave_with_pay_dates:
                    elif leave_with_pay_hour > 0:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
                            'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
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
                            'work_day_days': round(((-1) * not_day) - leave_with_pay - leave_with_out_pay, 2),
                            'work_day_hour': round(((-1) * not_hour) - (leave_with_pay * standard_work_hour) - (
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



                    else:
                        result['8'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round((-1) * not_day, 2),
                            'work_day_hour': round((-1) * not_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }


                else:

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
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    if leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
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
            number_of_weekday_actual=len([day for week in monthcal for day in week if \
                                     day.weekday() in weekend_day and \
                                     day.month == month])
            weekday_dates = [day for week in monthcal for day in week if \
                             day.weekday() in weekend_day and \
                             day.month == month]

            if self.struct_id.structure_type == 'basic_pay_office_stuff':
                monthly_total_work_hour = sum(self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                     ('date_start', '<=', self.date_to)]).mapped('duration'))
                # count_day_monthly_total_work_hour = self.env['hr.work.entry'].sudo().search_count(
                #     [('employee_id', '=', self.employee_id.id), ('date_start', '>=', self.date_from),
                #      ('date_start', '<=', self.date_to)])

            else:
                work_days_time = self.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
                     ('date', '<=', self.date_to), ('date', 'not in', weekday_dates)])
                monthly_total_work_hour = 0
                monthly_not_hour = 0
                work_date_dict = dict()
                for time in work_days_time:
                    if time.date not in work_date_dict.keys():
                        work_date_dict[time.date] = time.unit_amount
                    else:
                        work_date_dict[time.date] += time.unit_amount



                # for time in work_date_dict.keys():
                #     print(work_date_dict[time])
                #     if work_date_dict[
                #         time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                #         monthly_total_work_hour += work_date_dict[time]
                #     else:
                #         monthly_not_hour += work_date_dict[
                #                                 time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                #         monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

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
                 ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),('state','=','validate')], order='date_from')

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
                            [('employee_id', '=', self.employee_id.id), ('date', '=', weekend_date)]).mapped(
                            'unit_amount'))
                ph_day -= date_need_to_remove_from_holiday

            for time in work_date_dict.keys():
                if time not in public_holiday_dates:
                    print(work_date_dict[time])
                    if work_date_dict[
                        time] <= self.contract_id.structure_type_id.default_struct_id.standard_working_hour:
                        monthly_total_work_hour += work_date_dict[time]
                    else:
                        monthly_not_hour += work_date_dict[
                                                time] - self.contract_id.structure_type_id.default_struct_id.standard_working_hour
                        monthly_total_work_hour += self.contract_id.structure_type_id.default_struct_id.standard_working_hour

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
            leave_with_out_pay_datas = self.employee_id.get_leave_with_out_pay_datas(self.employee_id.id, self.date_from,
                                                                              self.date_to)
            leave_with_out_pay = leave_with_out_pay_hour / standard_work_hour

            public_holidays = self.env['hr.leave'].sudo().search(
                [('mode_company_id', '=', self.company_id.id),
                 ('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to), ('state', '=', 'validate')],
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

            #######Leave With Out Pay###########
            net_working_day = calendar_days - number_of_weekday-weekday_not_consider - ph_day
            net_working_hour = round(
                calendar_days * standard_work_hour - number_of_weekday * standard_work_hour-weekday_not_consider* standard_work_hour- ph_day * standard_work_hour,
                2)
            HOT_day = ph_day
            # HOT_Hour = round(ph_day * standard_work_hour, 2)
            HOT_Hour = round(public_holiday_work_hour, 2) - round(work_hour_need_to_remove, 2)

            monthly_total_day = monthly_actual_timesheet_hour / standard_work_hour
            monthly_total_hour = round(monthly_actual_timesheet_hour, 2)
            # monthly_total_day = monthly_total_work_hour / standard_work_hour
            # monthly_total_hour = round(monthly_total_work_hour, 2)

            net_worked_day = monthly_total_work_hour / standard_work_hour
            net_worked_hour = round(monthly_total_work_hour, 2)
            # net_worked_day = monthly_total_day - HOT_day
            # net_worked_hour = round(monthly_total_hour - HOT_Hour, 2)

            actual_need_to_work = net_working_hour
            but_emp_work = monthly_total_work_hour - HOT_Hour
            extra_time_work = 0
            # if but_emp_work>actual_need_to_work:
            extra_time_work = but_emp_work - actual_need_to_work

            not_hour = round(monthly_not_hour, 2)
            not_day = monthly_not_hour / standard_work_hour
            # not_hour = extra_time_work
            # not_day = extra_time_work / standard_work_hour
            # not_hour=weekend_work_hour
            # not_day=not_hour/8
            if net_working_hour>net_worked_hour:
                absent_hour = round(net_working_hour - net_worked_hour, 2)
                absent_day = (net_working_hour - net_worked_hour) / standard_work_hour
            else:
                absent_hour=0
                absent_day=0
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
                'work_day_type': "Weekend Not Consider",
                'work_day_days': round(float(extra_weekday), 2),
                'work_day_hour': round(extra_weekday * standard_work_hour, 2),
                'work_day_formula': 'number of weekend not Consider days x {} hrs'.format(standard_work_hour)

            }
            result['4'] = {
                'work_day_id': self.id,
                'work_day_type': "Holiday",
                'work_day_days': round(float(HOT_day), 2),
                # 'work_day_hour': round(public_holiday_only, 2),
                'work_day_hour': round(HOT_day * standard_work_hour, 2),
                'work_day_formula': 'number of holiday days x {} hrs'.format(standard_work_hour)

            }
            result['5'] = {
                'work_day_id': self.id,
                'work_day_type': "Net Working (d/h)",
                'work_day_days': round(float(net_working_day), 2),
                'work_day_hour': round(net_working_hour, 2),
                'work_day_formula': 'calendar working (d/h) - weekend (d/h) - public working (d/h)'

            }

            result['6'] = {
                'work_day_id': self.id,
                'work_day_type': "Net Worked (d/h)",
                'work_day_days': round(net_worked_day, 2),
                'work_day_hour': round(net_worked_hour, 2),
                'work_day_formula': 'acutal ts duration (d/h) - weekend (d/h) - public working (d/h)'

            }
            if self.struct_id.structure_type == 'basic_pay_office_stuff':
                result['7'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Actual WE Duration (d/h)",
                    'work_day_days': round(monthly_total_day, 2),
                    'work_day_hour': round(monthly_total_hour, 2),
                    'work_day_formula': 'from work entry : std (d/h) + worked in weekend (d/h) + worked in public working (d/h)'
                }
            else:
                result['7'] = {
                    'work_day_id': self.id,
                    'work_day_type': "Actual Timesheet Duration (d/h)",
                    'work_day_days': round(monthly_total_day, 2),
                    'work_day_hour': round(monthly_total_hour, 2),
                    'work_day_formula': 'from timesheet : std (d/h) + worked in weekend (d/h) + worked in public working (d/h)'
                }

            result['8'] = {
                'work_day_id': self.id,
                'work_day_type': "HOT Worked (d/h)",
                # 'work_day_days': round(HOT_day,2),
                'work_day_days': round(HOT_Hour / standard_work_hour, 2),
                'work_day_hour': round(HOT_Hour, 2),
                'work_day_formula': 'from timesheet : worked in weekend (d/h) + worked in public working (d/h)'

            }
            # half day work calculation purpose
            if self.struct_id.structure_type == 'basic_pay_office_stuff':
                if not_hour > 0 and absent_hour == 0:
                    result['9'] = {
                        'work_day_id': self.id,
                        'work_day_type': "NOT Worked (d/h)",
                        'work_day_days': round(not_day, 2),
                        'work_day_hour': round(not_hour, 2),
                        'work_day_formula': 'net worked(d/h) - net working(d/h)'

                    }
                elif not_hour > 0 and absent_hour > 0:
                    result['9'] = {
                        'work_day_id': self.id,
                        'work_day_type': "NOT Worked (d/h)",
                        'work_day_days': round(not_day, 2),
                        'work_day_hour': round(not_hour, 2),
                        'work_day_formula': 'net worked(d/h) - net working(d/h)'

                    }
                    if leave_with_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h)'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['12'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    # elif leave_with_out_pay_dates:
                    if leave_with_out_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay + extra_weekday-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour) + extra_weekhour-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['12'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    # elif leave_with_pay_dates and leave_with_out_pay_dates:
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay + extra_weekday-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour) + extra_weekhour-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['12'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['13'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    if leave_with_pay_hour == 0 and leave_with_out_pay_hour == 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }

                if not_hour == 0 and absent_hour > 0:
                    if leave_with_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h)'

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
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }

                    # elif leave_with_out_pay_dates:
                    if leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay + extra_weekday-(half_day_consider_hour/standard_work_hour), 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour) + extra_weekhour-half_day_consider_hour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    # elif leave_with_pay_dates and leave_with_out_pay_dates:
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(absent_day - leave_with_pay - leave_with_out_pay + extra_weekday-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour) + extra_weekhour-half_day_consider_hour, 2),
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
                        result['12'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
                    if leave_with_pay_hour == 0 and leave_with_out_pay_hour == 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(absent_day-(half_day_consider_hour/standard_work_hour), 2),
                            'work_day_hour': round(absent_hour-half_day_consider_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Half Day Consider Time",
                            'work_day_days': round((half_day_consider_hour / standard_work_hour), 2),
                            'work_day_hour': round(half_day_consider_hour, 2),
                            'work_day_formula': 'from work entry'

                        }
            else:
                if not_hour > 0 and absent_hour == 0:
                    result['9'] = {
                        'work_day_id': self.id,
                        'work_day_type': "NOT Worked (d/h)",
                        'work_day_days': round(not_day, 2),
                        'work_day_hour': round(not_hour, 2),
                        'work_day_formula': 'net worked(d/h) - net working(d/h)'

                    }
                elif not_hour > 0 and absent_hour > 0:
                    result['9'] = {
                        'work_day_id': self.id,
                        'work_day_type': "NOT Worked (d/h)",
                        'work_day_days': round(not_day, 2),
                        'work_day_hour': round(not_hour, 2),
                        'work_day_formula': 'net worked(d/h) - net working(d/h)'

                    }
                    if leave_with_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour), 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h)'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    # elif leave_with_out_pay_dates:
                    if leave_with_out_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay+extra_weekday, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)+extra_weekhour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    # elif leave_with_pay_dates and leave_with_out_pay_dates:
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay+extra_weekday, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)+extra_weekhour, 2)),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }
                        result['11'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Pay",
                            'work_day_days': round(leave_with_pay, 2),
                            'work_day_hour': (round(leave_with_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                        result['12'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Leave With Out Pay",
                            'work_day_days': round(leave_with_out_pay, 2),
                            'work_day_hour': (round(leave_with_out_pay, 2) * standard_work_hour),
                            'work_day_formula': 'from timesheet'

                        }
                    if leave_with_pay_hour == 0 and leave_with_out_pay_hour == 0:
                        result['10'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(absent_day, 2),
                            'work_day_hour': round(absent_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }

                if not_hour == 0 and absent_hour > 0:
                    if leave_with_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour), 2)),
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
                    if leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay+extra_weekday, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)+extra_weekhour, 2)),
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
                    if leave_with_pay_hour > 0 and leave_with_out_pay_hour > 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': abs(round(absent_day - leave_with_pay - leave_with_out_pay+extra_weekday, 2)),
                            'work_day_hour': abs(round(absent_hour - (leave_with_pay * standard_work_hour) - (
                                    leave_with_out_pay * standard_work_hour)+extra_weekhour, 2)),
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
                    if leave_with_pay_hour == 0 and leave_with_out_pay_hour == 0:
                        result['9'] = {
                            'work_day_id': self.id,
                            'work_day_type': "Absent",
                            'work_day_days': round(absent_day, 2),
                            'work_day_hour': round(absent_hour, 2),
                            'work_day_formula': 'net worked(d/h) - net working(d/h) - leave with pay -leave without pay'

                        }


        return result.values()

    def get_payment_data(self):
        val_list=[]
        month=format_date(self.env, self.date_from, date_format="MMMM")
        balance = 0
        if self.move_id:
            credit_balance=self.move_id.line_ids.filtered(lambda acc: acc.account_root_id.id == 50054)
            for line in credit_balance:
                balance += line.credit
                vals={
                    'month':month,
                    'ref':self.move_id.name,
                    'debit':0,
                    'credit':line.credit,
                    'balance':balance
                }
                val_list.append(vals)

        if self.payment_move_ids:
            for move in self.payment_move_ids:
                for line in move.line_ids.filtered(lambda acc: acc.account_root_id.id == 50054):
                    balance -= line.debit
                    vals = {
                        'month': month,
                        'ref': move.name,
                        'debit': line.debit,
                        'credit': 0,
                        'balance': balance
                    }
                    val_list.append(vals)
        return val_list

    def get_payment_signature(self):
        get_model=self.env['ir.model'].sudo().search([('model','=','signature.setup')])
        if get_model:
            get_signature_data=self.env['signature.setup'].search([('model','=','hr.payslip'),('company_id','=',self.env.company.id)])
            return  get_signature_data
        else:
            return []








class HrPayslipWorkedDaysInherit(models.Model):
    _inherit = 'hr.payslip.worked_days'

    calendar_days=fields.Float(string="Calendar W/D")
    calendar_hours=fields.Float(string="Calendar W/H")

    weekend_days = fields.Float(string="Weekend W/D")
    weekend_hours = fields.Float(string="Weekend W/H")

    public_holidays = fields.Float(string="Public Holidays")
    public_holidays_hours = fields.Float(string="Public Holidays  Hours")



class SalaryPackage(models.Model):
    _name = 'employee.salary.package'

    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    type = fields.Char(string="Type")
    amount = fields.Float(string="Amount")

class HRPayslipHourlyLine(models.Model):
    _name="hr.payslip.hourly.line"

    hour_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')

    name = fields.Char(required=True, translate=True)
    note = fields.Text(string='Description')
    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(required=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                            "In that case, it is case sensitive.")

    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    amount = fields.Float(digits='Payroll')
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)

    amount_select = fields.Selection(related='salary_rule_id.amount_select', readonly=True)
    amount_fix = fields.Float(related='salary_rule_id.amount_fix', readonly=True)
    amount_percentage = fields.Float(related='salary_rule_id.amount_percentage', readonly=True)
    appears_on_payslip = fields.Boolean(related='salary_rule_id.appears_on_payslip', readonly=True)
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)
    partner_id = fields.Many2one(related='salary_rule_id.partner_id', readonly=True, store=True)

    date_from = fields.Date(string='From', related="hour_id.date_from", store=True)
    date_to = fields.Date(string='To', related="hour_id.date_to", store=True)
    company_id = fields.Many2one(related='hour_id.company_id')

    hour=fields.Float(string="Hour")
    hour_rate=fields.Float(string="Rate")

    @api.depends('hour', 'amount', 'hour_rate')
    def _compute_total(self):
        for line in self:
            line.total = line.amount
class WorkingHoursCal(models.Model):
    _name = 'working.hours.calc'

    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    work_days_cal_type = fields.Char(string="Type")
    work_days_cal_hour = fields.Char(string="Hour")
    work_days_cal_days = fields.Char(string="Days")

class WorkingDaysInputs(models.Model):
    _name = 'working.days.inputs'

    work_day_id = fields.Many2one('hr.payslip', string='Work Day', required=True, ondelete='cascade')
    work_day_type = fields.Char(string="Type")
    work_day_days = fields.Char(string="Days", digits=(16, 2))
    work_day_hour = fields.Char(string="Hour", digits=(16, 2))
    work_day_formula=fields.Char(string="Formula")


class HrPayslipLineInherit(models.Model):
    _inherit = 'hr.payslip.line'

    hours=fields.Float(string="Hours")
    rate_per_hours=fields.Float(string="Rate/Hour")
    ot_rate=fields.Float(string="Wages Ratio")





