from odoo import api, models, fields, _
import io
import base64
import xlsxwriter

from odoo.exceptions import ValidationError
from odoo.release import product_name


class CTCReportFormula(models.Model):
    _name = 'ctc.report.formula'
    _description = 'Employee CTC Reports and Formulas'

    @api.depends('ctc_line_ids')
    def _get_total_ctc_line_ids(self):
        for record in self:
            record.total_ctc_line_ids = len(record.ctc_line_ids)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Automatically updates `ctc_line_ids` when the company changes."""
        if self.company_id:
            # Fetch CTC lines for the selected company
            ctc_lines = self.env['ctc.report.formula.line'].search([
                ('company_id', '=', self.company_id.id)
            ])
            self.ctc_line_ids = [(6, 0, ctc_lines.ids)]  # Replace all current records with the fetched ones

    # @api.depends('ctc_line_ids')
    # def _get_total_ctc_line_ids(self):
    #     """Compute the total number of CTC lines."""
    #     # for record in self:
    #     #     record.total_ctc_line_ids = len(record.ctc_line_ids)


    # Fields
    name = fields.Char('Name', default='Employee CTC and Formulas', readonly=True)
    ctc_line_ids = fields.One2many('ctc.report.formula.line', 'ctc_id', 'CTC Lines')
    total_ctc_line_ids = fields.Integer('Total CTC', compute=_get_total_ctc_line_ids, readonly=True)

    # formula Fields
    formula_for_leave_salary = fields.Char('Formula For Leave Salary', default='%(salary)s/11')
    formula_for_gratuity = fields.Char('Formula For Gratuity', default='%(salary)s/12')
    formula_for_air_fare = fields.Char('Formula For Air Fare', default='4000/12')
    formula_for_medical_insurance = fields.Char('Formula For Medical Insurance', default='1500/12')
    formula_for_visa_cost = fields.Char('Formula For Visa Cost', default='8000/24')
    formula_for_rent = fields.Char('Formula For Camp/House Rent', default='%(houserent)s', readonly=True)
    rent_accom1 = fields.Float('Rent For Accom 1', default=0.0)
    rent_accom2 = fields.Float('Rent For Accom 2', default=0.0)
    filter_structure_type_id = fields.Many2one(
        'hr.payroll.structure.type',
        string='Filter Structure',
        required=False,  # Optional: Make it not mandatory
        help='Select the payroll structure type to filter contracts'
    )

    def action_reset_ctc_line(self):
        all_ctc_line = self.env['ctc.report.formula.line'].search([])
        all_ctc_line.unlink()
        self.action_create_ctc_line()


    @api.model
    def action_create_ctc_line(self):
        all_contract_ids = self.env['hr.contract'].search([
            ('state', '=', 'open'),
            ('company_id', '=', self.env.company.id)
        ])
        print(all_contract_ids)
        all_ctc_line_ids = self.env['ctc.report.formula.line'].search([])
        ctc_id = self.env['ctc.report.formula'].search([], limit=1)
        if all_contract_ids:
            for contract in all_contract_ids:
                vals = {
                    'employee_id': contract.employee_id.id,
                    'contract_id': contract.id,
                    'salary': contract.wage,
                    'house_rent': contract.house_rent,
                    'ctc_id': ctc_id.id
                }
                # Correct domain syntax
                ctc_line = self.env['ctc.report.formula.line'].search([('employee_id', '=', contract.employee_id.id)],
                                                                      limit=1)
                if ctc_line and ctc_line in all_ctc_line_ids:
                    ctc_line.write(vals)
                elif not ctc_line:  # Simplified to `elif` since `ctc_line` is None
                    self.env['ctc.report.formula.line'].create(vals)


    # def write(self, vals):
    #     self.env['ctc.report.formula.line'].compute_all_fields()
    #     return super(CTCReportFormula, self).write(vals)


    def action_launch_create_deferred_expense_wizard(self):
        return self.env.ref('bi_employee_payslip_report.action_create_deferred_expense_wizard').read()[0]

    @api.onchange('filter_structure_type_id')
    def filter_ctc_lines(self):
        if self.filter_structure_type_id:
            self.ctc_line_ids = False

            filtered_ctc_lines = self.env['ctc.report.formula.line'].search([
                ('employee_id', '=', self.filter_structure_type_id.id)
            ])

            if filtered_ctc_lines:
                self.write({
                    'ctc_line_ids': [(4, line.id) for line in filtered_ctc_lines]
                })

    def action_print_xls(self):
        # Prepare in-memory file
        output = io.BytesIO()

        # Create a workbook and worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('CTC Report')

        # Define formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#F9DA04', 'border': 1})
        data_format = workbook.add_format({'border': 1, 'num_format': '0.00'})  # Two decimal places for float numbers

        # Define headers
        headers = [
            'Employee', 'Total', 'Total Cash Salary', 'Salary', 'Other Salary', 'Other Costs',
            'Leave Salary', 'Gratuity', 'Air Fare', 'Medical Insurance', 'Visa Cost', 'House Rent'
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Populate data rows
        row = 1
        for line in self.ctc_line_ids:
            worksheet.write(row, 0, line.employee_id.name or '', data_format)
            worksheet.write(row, 1, line.total or 0, data_format)
            worksheet.write(row, 2, line.total_cash_salary or 0, data_format)
            worksheet.write(row, 3, line.salary or 0, data_format)
            worksheet.write(row, 4, line.other_salary or 0, data_format)
            worksheet.write(row, 5, line.other_costs or 0, data_format)
            worksheet.write(row, 6, line.leave_salary or 0, data_format)
            worksheet.write(row, 7, line.gratuity or 0, data_format)
            worksheet.write(row, 8, line.air_fare or 0, data_format)
            worksheet.write(row, 9, line.medical_insurance or 0, data_format)
            worksheet.write(row, 10, line.visa_cost or 0, data_format)
            worksheet.write(row, 11, line.house_rent or 0, data_format)
            row += 1

        # Close the workbook
        workbook.close()

        # Prepare file download
        output.seek(0)
        xls_file = output.read()
        output.close()

        # Encode the file in base64
        encoded_file = base64.b64encode(xls_file).decode()

        # Create an attachment record
        attachment = self.env['ir.attachment'].create({
            'name': 'Employee CTC Report.xlsx',  # Set the filename
            'type': 'binary',
            'datas': encoded_file,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': self._name,
            'res_id': self.id,
        })

        # Return action to download the attachment
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }




class CTCReportsAndFormulaLine(models.Model):
    _name = 'ctc.report.formula.line'
    _description = 'Employee CTC Reports and Formulas Lines'

    def _compute_total(self):
        for rec in self:
            rec.total = rec.total_cash_salary + rec.other_costs

    def _compute_total_cash_salary(self):
        for rec in self:
            rec.total_cash_salary = rec.salary + rec.other_salary

    def _compute_other_costs(self):
        for rec in self:
            rec.other_costs = rec.leave_salary + rec.gratuity + rec.air_fare + rec.medical_insurance + rec.visa_cost + rec.house_rent

    # Fields definition
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    contract_id = fields.Many2one('hr.contract', 'Contract')

    salary = fields.Integer('Basic Salary', readonly=False, store=True)
    leave_salary = fields.Float('Leave Salary', readonly=False, store=True)
    gratuity = fields.Float('Gratuity', readonly=False, store=True)
    air_fare = fields.Float('Air Fare', readonly=False, store=True)
    medical_insurance = fields.Float('Medical Insurance', readonly=False, store=True)
    visa_cost = fields.Float('Visa Cost', readonly=False, store=True)
    house_rent = fields.Float('Camp/House Rent', readonly=False, store=True)
    total = fields.Float('Total-CTC', readonly=True, compute=_compute_total)
    other_salary = fields.Float('Other Salary', readonly=False, store=True)
    total_cash_salary = fields.Float('CTC-Cash', readonly=True,  compute=_compute_total_cash_salary)
    other_costs = fields.Float('CTC-Others', readonly=True,  compute=_compute_other_costs)
    company_id = fields.Many2one('res.company', 'Company', readonly=False, related='employee_id.company_id')


    # Relation
    ctc_id = fields.Many2one('ctc.report.formula', 'CTC', readonly=False)

    # Methods
    def update_salary(self):
        for rec in self:
            if rec.contract_id:
                rec.salary = rec.contract_id.wage or 0

    def compute_all_fields(self):
        for rec in self:
            # Compute Leave Salary
            if rec.salary and rec.ctc_id.formula_for_leave_salary and '%(salary)s' in rec.ctc_id.formula_for_leave_salary:
                leave_salary_formula = rec.ctc_id.formula_for_leave_salary.replace('%(salary)s', str(rec.salary))
                try:
                    rec.leave_salary = eval(leave_salary_formula)
                except:
                    rec.leave_salary = 0.0
            else:
                rec.leave_salary = 0.0

            # Compute Gratuity
            if rec.salary and rec.ctc_id.formula_for_gratuity and '%(salary)s' in rec.ctc_id.formula_for_gratuity:
                gratuity_formula = rec.ctc_id.formula_for_gratuity.replace('%(salary)s', str(rec.salary))
                try:
                    rec.gratuity = eval(gratuity_formula)
                except:
                    rec.gratuity = 0.0
            else:
                rec.gratuity = 0.0

            # Compute Air Fare
            if rec.ctc_id.formula_for_air_fare:
                try:
                    rec.air_fare = eval(rec.ctc_id.formula_for_air_fare)
                except:
                    rec.air_fare = 0.0
            else:
                rec.air_fare = 0.0

            # Compute Medical Insurance
            if rec.ctc_id.formula_for_medical_insurance:
                try:
                    rec.medical_insurance = eval(rec.ctc_id.formula_for_medical_insurance)
                except:
                    rec.medical_insurance = 0.0
            else:
                rec.medical_insurance = 0.0

            # Compute Visa Cost
            if rec.ctc_id.formula_for_visa_cost:
                try:
                    rec.visa_cost = eval(rec.ctc_id.formula_for_visa_cost)
                except:
                    rec.visa_cost = 0.0
            else:
                rec.visa_cost = 0.0



            # Compute House Rent
            contract_id = self.env['hr.contract'].sudo().search([('id', '=', rec.employee_id.contract_id.id)], limit=1)
            if contract_id and contract_id.house_rent > 0:
                rec.house_rent = contract_id.house_rent or 0.0
            elif contract_id and contract_id.house_rent <= 0:
                if rec.employee_id.accommodation == 'accom1':
                    rec.house_rent = eval(str(rec.ctc_id.rent_accom1))
                elif rec.employee_id.accommodation == 'accom2':
                    rec.house_rent = eval(str(rec.ctc_id.rent_accom2))
                else:
                    rec.house_rent = 0.0

            # Compute Other Salary
            if contract_id:
                rec.other_salary = contract_id.monthly_yearly_costs - contract_id.wage - contract_id.house_rent
            else:
                rec.other_salary = 0.0

    @api.model
    def create(self, vals_list):
        # Call the super method to create the record(s)
        records = super(CTCReportsAndFormulaLine, self).create(vals_list)
        # Call the computation method
        records.compute_all_fields()

        return records

    def write(self, vals):
        # Check if the context prevents compute to avoid recursion
        if not self.env.context.get('skip_compute', False):
            # Temporarily set a context to skip further computation during write
            self.with_context(skip_compute=True).compute_all_fields()
        return super(CTCReportsAndFormulaLine, self).write(vals)

    def update_salary(self):
        for rec in self:
            if rec.contract_id:
                rec.salary = rec.contract_id.wage or 0

    @api.model
    def create_ctc_line(self):
        print('executing create_ctc_line')
        all_ctc = self.env['ctc.report.formula.line'].sudo().search([])
        all_ctc.unlink()
        all_employee_ids = self.env['hr.employee'].search([
            ('company_id', '=', self.env.company.id)
        ])
        for employee in all_employee_ids:
            ctc_line = self.env['ctc.report.formula.line'].sudo().search([('employee_id', '=', employee.id)], limit=1)
            if not ctc_line:
                self.env['ctc.report.formula.line'].create({
                    'employee_id': employee.id,
                })
        self._check_and_delete()

    def _check_and_delete(self):
        ctc_lines = self.search([])
        for line in ctc_lines:
            if not line.employee_id:
                line.unlink()



    # def default_get(self, fields_list):
    #     res = super(CTCReportsAndFormulaLine, self).default_get(fields_list)
    #     res.update({
    #         'company_id': self.env.company.id
    #     })
    #     return res


class HRContract(models.Model):
    _inherit = 'hr.contract'
