from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    food_allowance = fields.Float('Food Allowance')
    vehicle_allowance = fields.Float('Vehicle Allowance')
    telephone_allowance = fields.Float('Telephone Allowance')
    other_allowance = fields.Float('other Allowances')
    wps_salary = fields.Float('WPS Salary')
    house_rent = fields.Float('Camp/House Rent')
    # not_per_hour= fields.Float('NOT Per Hour', compute="_get_hot_not_salary" ,default=0,readonly=False)
    # hot_per_hour= fields.Float('HOT Per Hour',compute="_get_hot_not_salary" ,default=0,readonly=False)

    not_per_hour = fields.Float('NOT Per Hour',  default=0, readonly=False)
    hot_per_hour = fields.Float('HOT Per Hour',  default=0, readonly=False)

    wage = fields.Monetary('Basic Salary', required=True, tracking=True, help="Employee's monthly gross wage.")
    monthly_yearly_costs = fields.Monetary(compute='_compute_monthly_yearly_costs', string='Monthly Equivalent Cost',
                                           readonly=True,
                                           help="Total monthly cost of the employee for the employer.")

    final_yearly_costs = fields.Monetary(compute='_compute_final_yearly_costs',
                                         readonly=False, store=True,
                                         string="Employee Budget",
                                         tracking=True,
                                         help="Total yearly cost of the employee for the employer.")
    salary_per_h = fields.Float(string="Salary per Hour", compute="_get_hot_not_salary",default=0)
    is_on_gross_sph = fields.Boolean('On Gross', default=False) #Handle salary per hor on gross or basic salary
    wps_salary = fields.Float('WPS Salary')
    not_rate = fields.Float('Not Rate')
    hot_rate = fields.Float('Hot Rate')

    @api.model
    def default_get(self, fields_list):
        res = super(HrContract, self).default_get(fields_list)
        get_last_hr_contract = self.env['hr.contract'].search([], limit=1, order="id desc")
        if get_last_hr_contract:
            res.update({
                'is_on_gross_sph': get_last_hr_contract.is_on_gross_sph
            })
        return res

    # @api.depends('structure_type_id')
    # def _set_hot_not_rate(self):
    #     for rec in self:
    #         rec.not_rate=rec.structure_type_id.default_struct_id.not_rate
    #         rec.hot_rate=rec.structure_type_id.default_struct_id.hot_rate

    # @api.onchange('not_rate','hot_rate')
    # def _set_not_hot_per_hour(self):
    #     for rec in self:
    #         rec.not_per_hour=rec.salary_per_h*rec.not_rate
    #         rec.hot_per_hour=rec.salary_per_h*rec.hot_rate

    @api.onchange('not_per_hour','hot_per_hour')
    def set_hot_not_rate(self):
        for rec in self:
            if rec.salary_per_h>0:
                rec.hot_rate= rec.hot_per_hour/rec.salary_per_h
                rec.not_rate=rec.not_per_hour/rec.salary_per_h
            else:
                rec.hot_rate = 0
                rec.not_rate = 0


    @api.model
    def action_set_contact_default_hot_not(self):
        get_all_company = self.env['res.company'].sudo().search([])
        for com in get_all_company:
            get_all_contract = self.env['hr.contract'].sudo().search([('company_id','=',com.id)])

            for rec in get_all_contract:
                if not rec.not_rate or rec.not_rate == 0:
                    rec.not_rate = rec.structure_type_id.default_struct_id.not_rate
                if not rec.hot_rate or rec.hot_rate == 0:
                    rec.hot_rate =  rec.structure_type_id.default_struct_id.hot_rate


    @api.onchange('is_on_gross_sph')
    @api.depends('wage','wage_type','not_rate','hot_rate')
    def _get_hot_not_salary(self):
        for rec in self:
            _logger.info(rec.is_on_gross_sph)
            if rec.wage_type=='monthly':
                standard_working_hour=rec.structure_type_id.default_struct_id.standard_working_hour
                if rec.is_on_gross_sph:
                    rec.salary_per_h=rec.monthly_yearly_costs*12/365/(standard_working_hour if standard_working_hour>0 else 8)
                else:
                    rec.salary_per_h=rec.wage*12/365/(standard_working_hour if standard_working_hour>0 else 8)
                if rec.not_rate>0:
                    rec.not_per_hour = rec.salary_per_h * rec.not_rate
                else:
                    rec.not_rate=rec.structure_type_id.default_struct_id.not_rate
                    rec.not_per_hour = rec.salary_per_h * rec.structure_type_id.default_struct_id.not_rate
                if rec.hot_rate>0:
                    rec.hot_per_hour = rec.salary_per_h * rec.hot_rate
                else:
                    rec.hot_rate = rec.structure_type_id.default_struct_id.hot_rate
                    rec.hot_per_hour = rec.salary_per_h * rec.structure_type_id.default_struct_id.hot_rate
                # rec.not_per_hour=rec.salary_per_h*rec.structure_type_id.default_struct_id.not_rate
                # rec.hot_per_hour=rec.salary_per_h*rec.structure_type_id.default_struct_id.hot_rate



            else:
                rec.salary_per_h=0
                rec.not_per_hour=0
                rec.hot_per_hour=0
                rec.not_rate=0
                rec.hot_rate=0

    @api.depends('wage', 'food_allowance', 'vehicle_allowance', 'telephone_allowance', 'other_allowance','house_rent')
    def _compute_monthly_yearly_costs(self):
        for contract in self:
            contract.monthly_yearly_costs = contract.wage + contract.food_allowance + contract.vehicle_allowance + \
                                            contract.telephone_allowance + contract.other_allowance+contract.house_rent
            # contract.final_yearly_costs = contract.monthly_yearly_costs * 12
            # contract.wage=contract.wage-0

    @api.onchange('monthly_yearly_costs')
    def _compute_final_yearly_costs(self):
        for contract in self:
            contract.final_yearly_costs = contract.monthly_yearly_costs * 12

    @api.onchange('final_yearly_costs')
    def _onchange_final_yearly_costs(self):
        self.wage = self.wage
