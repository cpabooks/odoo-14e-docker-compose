from odoo import api, models, fields, _


class SalaryCodeSetup(models.Model):
    _name = 'salary.code.setup'

    salary_structure = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    # company_id=fields.Many2one('res.company',default=lambda self:self.env.company.id)
    code_line = fields.One2many('salary.code.setup.line', 'code_setup_id')

    @api.onchange('salary_structure')
    def get_salary_code(self):
        if self.salary_structure:
            self.code_line = [(5, 0, 0)]
            get_all_attach_rules = self.env['hr.salary.rule'].search([('struct_id', '=', self.salary_structure.id)])
            # if struct.name=='Hourly Pay on Basic':
            rule_list = []
            if self.salary_structure.name == 'Hourly Pay on Basic':
                for rule in get_all_attach_rules:
                    line_data = (0, 0, {
                        'existing_rule': rule.id,
                        'python_code': rule.amount_python_compute,
                    })
                    if rule.name == 'Basic Salary':
                        line_data[2]['propose_code'] = 'result=contract.wage'
                    if rule.name == 'Other Allowance':
                        line_data[2]['propose_code'] = 'result = contract.other_allowance'
                    if rule.name == 'Food Allowance':
                        line_data[2]['propose_code'] = 'result = contract.food_allowance'
                    if rule.name == 'Telephone Allowance':
                        line_data[2]['propose_code'] = 'result = contract.telephone_allowance'
                    if rule.name == 'Vehicle Allowance':
                        line_data[2]['propose_code'] = 'result = contract.vehicle_allowance'
                    if rule.name == 'NOT Salary':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from, payslip.date_to)*payslip.contract_id.not_rate*contract.salary_per_h'
                    if rule.name == 'HOT Salary':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_hot_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.hot_rate*contract.salary_per_h'
                    if rule.name == 'Absent':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.not_rate'
                    if rule.name == 'Leave With Pay':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_leave_with_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
                    if rule.name == 'Leave With Out Pay':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_leave_with_out_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
                    if rule.name == 'Gross':
                        line_data[2][
                            'propose_code'] = 'result = categories.BASIC + categories.ALW+categories.HOTSAL + categories.NOTSAL'
                    if rule.name == 'Extra Effort':
                        line_data[2]['propose_code'] = 'result = payslip.extra_amount'
                    if rule.name == 'Deduction':
                        line_data[2]['propose_code'] = 'result = payslip.deduction_amount'

                    if rule.name == 'Net Salary':
                        line_data[2][
                            'propose_code'] = 'result = categories.BASIC + categories.ALW +categories.HOTSAL+categories.NOTSAL-categories.ABSENT+categories.LWP-categories.LWOP+categories.EXTRA-categories.DED'

                    rule_list.append(line_data)
            elif self.salary_structure.name == 'Hourly Pay on Timesheet':
                for rule in get_all_attach_rules:
                    line_data = (0, 0, {
                        'existing_rule': rule.id,
                        'python_code': rule.amount_python_compute,
                    })
                    # if rule.name == 'Basic Salary':
                    #     line_data[2]['propose_code'] = 'result=contract.hourly_wage'
                    if rule.name == 'Hourly Pay on Timesheet':
                        line_data[2]['propose_code'] = 'result=contract.hourly_wage'
                    if rule.name == 'Other Allowance':
                        line_data[2]['propose_code'] = 'result = contract.other_allowance'
                    if rule.name == 'Food Allowance':
                        line_data[2]['propose_code'] = 'result = contract.food_allowance'
                    if rule.name == 'Telephone Allowance':
                        line_data[2]['propose_code'] = 'result = contract.telephone_allowance'
                    if rule.name == 'Vehicle Allowance':
                        line_data[2]['propose_code'] = 'result = contract.vehicle_allowance'
                    if rule.name == 'NOT Salary':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from, payslip.date_to)*payslip.contract_id.not_rate*contract.salary_per_h'
                    if rule.name == 'HOT Salary':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_hot_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.hot_rate*contract.salary_per_h'
                    if rule.name == 'Absent':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.not_rate'
                    if rule.name == 'Leave With Pay':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_leave_with_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
                    if rule.name == 'Leave With Out Pay':
                        line_data[2][
                            'propose_code'] = 'result = employee.get_leave_with_out_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
                    if rule.name == 'Gross':
                        # line_data[2]['propose_code'] = 'result = categories.CHPOT + categories.ALW+categories.HOTSAL + categories.NOTSAL'
                        line_data[2]['propose_code'] = 'result = categories.CHPOT'
                    if rule.name == 'Extra Effort':
                        line_data[2]['propose_code'] = 'result = payslip.extra_amount'
                    if rule.name == 'Deduction':
                        line_data[2]['propose_code'] = 'result = payslip.deduction_amount'

                    if rule.name == 'Net Salary':
                        # line_data[2]['propose_code'] = 'result = categories.CHPOT + categories.ALW +categories.HOTSAL+categories.NOTSAL-categories.ABSENT+categories.LWP-categories.LWOP+categories.EXTRA-categories.DED'
                        line_data[2]['propose_code'] = 'result = categories.CHPOT'

                    rule_list.append(line_data)
            self.code_line = rule_list

    # @api.onchange('salary_structure')
    # def get_salary_code(self):
    #     if self.salary_structure:
    #         self.code_line = [(5, 0, 0)]
    #         get_all_attach_rules = self.env['hr.salary.rule'].search([('struct_id', '=', self.salary_structure.id)])
    #         # if struct.name=='Hourly Pay on Basic':
    #         rule_list = []
    #         for rule in get_all_attach_rules:
    #             line_data = (0, 0, {
    #                 'existing_rule': rule.id,
    #                 'python_code': rule.amount_python_compute,
    #             })
    #             if rule.name == 'Basic Salary':
    #                 line_data[2]['propose_code'] = 'result=contract.wage'
    #             if rule.name == 'Other Allowance':
    #                 line_data[2]['propose_code'] = 'result = contract.other_allowance'
    #             if rule.name == 'Food Allowance':
    #                 line_data[2]['propose_code'] = 'result = contract.food_allowance'
    #             if rule.name == 'Telephone Allowance':
    #                 line_data[2]['propose_code'] = 'result = contract.telephone_allowance'
    #             if rule.name == 'Vehicle Allowance':
    #                 line_data[2]['propose_code'] = 'result = contract.vehicle_allowance'
    #             if rule.name == 'NOT Salary':
    #                 line_data[2][
    #                     'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from, payslip.date_to)*payslip.contract_id.not_rate*contract.salary_per_h'
    #             if rule.name == 'HOT Salary':
    #                 line_data[2][
    #                     'propose_code'] = 'result = employee.get_hot_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.hot_rate*contract.salary_per_h'
    #             if rule.name == 'Absent':
    #                 line_data[2][
    #                     'propose_code'] = 'result = employee.get_not_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.not_rate'
    #             if rule.name == 'Leave With Pay':
    #                 line_data[2][
    #                     'propose_code'] = 'result = employee.get_leave_with_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
    #             if rule.name == 'Leave With Out Pay':
    #                 line_data[2][
    #                     'propose_code'] = 'result = employee.get_leave_with_out_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
    #             if rule.name == 'Gross':
    #                 line_data[2][
    #                     'propose_code'] = 'result = categories.BASIC + categories.ALW+categories.HOTSAL + categories.NOTSAL'
    #             if rule.name == 'Extra Effort':
    #                 line_data[2]['propose_code'] = 'result = payslip.extra_amount'
    #             if rule.name == 'Deduction':
    #                 line_data[2]['propose_code'] = 'result = payslip.deduction_amount'
    #
    #             if rule.name == 'Net Salary':
    #                 line_data[2][
    #                     'propose_code'] = 'result = categories.BASIC + categories.ALW +categories.HOTSAL+categories.NOTSAL-categories.ABSENT+categories.LWP-categories.LWOP+categories.EXTRA-categories.DED'
    #
    #             rule_list.append(line_data)
    #         self.code_line = rule_list

    def setup_code(self):
        for rec in self:
            if rec.salary_structure:
                for line in rec.code_line:
                    line.existing_rule.amount_python_compute = line.propose_code

    # @api.model
    # def default_setup_for_all_salary_structure(self):
    #     get_all_salary_structure=self.env['hr.payroll.structure'].sudo().search([])
    #     for struct in get_all_salary_structure:
    #         get_setup_exist_or_not=self.env['salary.code.setup'].search([('salary_structure','=',struct.id)])
    #         if not get_setup_exist_or_not:
    #             prepare_master={
    #                 'salary_structure':struct.id,
    #             }
    #             parent=self.env['salary.code.setup'].sudo().create(prepare_master)
    #
    #             get_all_attach_rules=self.env['hr.salary.rule'].search([('struct_id','=',struct.id)])
    #             # if struct.name=='Hourly Pay on Basic':
    #             rule_list=[]
    #             for rule in get_all_attach_rules:
    #                     line_data = {
    #                         'code_setup_id': parent.id,
    #                         'existing_rule': rule.id,
    #                         'python_code': rule.amount_python_compute,
    #                     }
    #                     if rule.name=='Basic Salary':
    #                             line_data[2]['propose_code']='result=contract.wage'
    #                     if rule.name=='Other Allowance':
    #                             line_data[2]['propose_code']='result = contract.other_allowance'
    #                     if rule.name=='Food Allowance':
    #                             line_data[2]['propose_code']='result = contract.food_allowance'
    #                     if rule.name=='Telephone Allowance':
    #                             line_data[2]['propose_code']='result = contract.telephone_allowance'
    #                     if rule.name=='Vehicle Allowance':
    #                             line_data[2]['propose_code']='result = contract.vehicle_allowance'
    #                     if rule.name=='NOT Salary':
    #                             line_data[2]['propose_code']='result = employee.get_not_overtime(employee.id, payslip.date_from, payslip.date_to)*payslip.contract_id.not_rate*contract.salary_per_h'
    #                     if rule.name=='HOT Salary':
    #                             line_data[2]['propose_code']='result = employee.get_hot_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.hot_rate*contract.salary_per_h'
    #                     if rule.name=='Absent':
    #                             line_data[2]['propose_code']='result = employee.get_not_overtime(employee.id, payslip.date_from,payslip.date_to)*payslip.contract_id.not_rate'
    #                     if rule.name=='Leave With Pay':
    #                             line_data[2]['propose_code']='result = employee.get_leave_with_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
    #                     if rule.name=='Leave With Out Pay':
    #                             line_data[2]['propose_code']='result = employee.get_leave_with_out_pay(employee.id, payslip.date_from,payslip.date_to)* contract.salary_per_h'
    #                     if rule.name=='Gross':
    #                             line_data[2]['propose_code']='result = categories.BASIC + categories.ALW+categories.HOTSAL + categories.NOTSAL'
    #                     if rule.name=='Net Salary':
    #                             line_data[2]['propose_code']='result = categories.BASIC + categories.ALW +categories.HOTSAL+categories.NOTSAL-categories.ABSENT'
    #
    #                     rule_list.append(line_data)
    #
    #             self.env['salary.code.setup.line'].sudo().create(rule_list)


class SalaryCodeSetupLine(models.Model):
    _name = 'salary.code.setup.line'

    code_setup_id = fields.Many2one('salary.code.setup')
    existing_rule = fields.Many2one('hr.salary.rule', string="Salary Rule")
    python_code = fields.Text(related="existing_rule.amount_python_compute")

    propose_code = fields.Text(string="Propose Code")