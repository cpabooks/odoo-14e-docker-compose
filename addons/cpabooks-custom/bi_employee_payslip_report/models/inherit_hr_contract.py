from odoo import models, fields, api,_


class InheritHRContract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='open')


    # wage = fields.Monetary('Basic Salary',required=True, tracking=True, help="Employee's monthly gross wage.")
    # monthly_yearly_costs = fields.Monetary(compute='_compute_monthly_yearly_costs', string='Monthly Equivalent Cost',
    #                                        readonly=True,
    #                                        help="Total monthly cost of the employee for the employer.")
    #
    # final_yearly_costs = fields.Monetary(compute='_compute_final_yearly_costs',
    #                                      readonly=False, store=True,
    #                                      string="Employee Budget",
    #                                      tracking=True,
    #                                      help="Total yearly cost of the employee for the employer.")
    # salary_per_h = fields.Float(string="Salary per Hour")
    # wps_salary = fields.Float('WPS Salary')

    # @api.depends(lambda self: (
    #         'structure_type_id.salary_advantage_ids.res_field_id',
    #         'structure_type_id.salary_advantage_ids.impacts_net_salary',
    #         *self._get_advantage_fields()))
    # def _compute_final_yearly_costs(self):

    weekend_day = fields.Many2many('week.day', string="Weekend")

    half_day= fields.Many2many('week.day','hr_contract_half_day_rel', string="Half Day")
    half_day_working_hour = fields.Float(string="Half Day Working Hour")

    @api.model
    def create(self, vals_list):
        res = super(InheritHRContract, self).create(vals_list)
        if res.state == 'open':
            ctc_id = self.env['ctc.report.formula'].search([],limit=1)
            self.env['ctc.report.formula.line'].create({
                'contract_id': self.id,
                'employee_id': self.employee_id.id,
                'salary': self.wage,
                'house_rent': self.house_rent,
                'ctc_id': ctc_id.id,
            })
        return res

    def write(self, vals):
        res = super(InheritHRContract, self).write(vals)
        print(vals)

        # Check if state is being updated or already in 'open'
        if 'state' in vals and vals['state'] == 'open' or self.state == 'open':
            if 'final_yearly_costs' in vals:
                self.env['ctc.report.formula.line'].compute_all_fields()
            if 'house_rent' in vals or 'wage' in vals or 'state' in vals:
                ctc_line = self.env['ctc.report.formula.line'].search([('contract_id', '=', self.id)], limit=1)
                ctc_id = self.env['ctc.report.formula'].search([], limit=1)
                update_vals = {
                    'ctc_id': ctc_id.id
                }

                if 'wage' in vals:
                    update_vals['salary'] = vals['wage']
                elif 'wage' not in vals:
                    update_vals['salary'] = self.wage  # Ensure current value is used if state changes

                if 'house_rent' in vals:
                    update_vals['house_rent'] = vals['house_rent']
                elif 'house_rent' not in vals:
                    update_vals['house_rent'] = self.house_rent  # Ensure current value is used if state changes

                if ctc_line:
                    ctc_line.write(update_vals)
                else:
                    # Create a new CTC line if not found
                    self.env['ctc.report.formula.line'].create({
                        'contract_id': self.id,
                        'employee_id': self.employee_id.id,
                        **update_vals,  # Add salary and house_rent values
                    })
        return res

    @api.model
    def action_create_ctc_line(self):
        all_contract_ids = self.env['hr.contract'].search([('state', '=', 'open')])
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

    # @api.depends('wage', 'food_allowance', 'vehicle_allowance', 'telephone_allowance', 'other_allowance')
    # def _compute_monthly_yearly_costs(self):
    #     for contract in self:
    #         contract.monthly_yearly_costs = contract.wage + contract.food_allowance + contract.vehicle_allowance + \
    #                                         contract.telephone_allowance + contract.other_allowance
    #         # contract.final_yearly_costs = contract.monthly_yearly_costs * 12
    #         # contract.wage=contract.wage-0
    #
    # @api.onchange('monthly_yearly_costs')
    # def _compute_final_yearly_costs(self):
    #     for contract in self:
    #         contract.final_yearly_costs = contract.monthly_yearly_costs*12
    #
    #
    # @api.onchange('final_yearly_costs')
    # def _onchange_final_yearly_costs(self):
    #     self.wage = self.wage

