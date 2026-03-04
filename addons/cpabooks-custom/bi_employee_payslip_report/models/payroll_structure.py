from odoo import models, fields, api


class PayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    not_rate= fields.Float('NOT Rate',default=1.25)
    hot_rate= fields.Float('HOT Rate',default=1.50)

    weekend_day=fields.Many2many('week.day',string="Weekend", default=lambda self: self.env['week.day'].search([('name', '=', 'SUNDAY')]))




    standard_working_hour=fields.Float(string="Standard Working Hour",default=8)

    half_day = fields.Many2many('week.day','hr_payroll_structure_half_day_rel', string="Half Day",
                                   default=lambda self: self.env['week.day'].search([('name', '=', 'SATURDAY')]))
    half_day_working_hour = fields.Float(string="Half Day Working Hour", default=5)

    company_mol_id = fields.Char(string="MOL ID")

    structure_type=fields.Selection([('basic_pay_office_stuff','Basic Pay Office Stuff')],string="Structure type")

    overtime_cal_method=fields.Selection([('on_daily','Daily Basis'),('on_monthly','Monthly Basis')],default='on_monthly',string="Overtime Calculation Method")
    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False, required=False,
                                 company_dependent=True,
                                 default=lambda self: self.env['account.journal'].sudo().search([
                                     ('type', '=', 'general'),('name','=','Salary Journal') ,('company_id', '=', self.env.company.id)], limit=1))

    @api.model
    def action_set_structure_default_value(self):
        get_all_structure=self.env['hr.payroll.structure'].search([])
        for rec in get_all_structure:
            if not rec.not_rate or rec.not_rate==0:
                rec.not_rate=1.25
            if not rec.hot_rate or rec.hot_rate==0:
                rec.hot_rate=1.50
            if not rec.weekend_day:
                rec.weekend_day=self.env['week.day'].search([('name', '=', 'SUNDAY')])
            if not rec.standard_working_hour or rec.standard_working_hour==0:
                rec.standard_working_hour=8
