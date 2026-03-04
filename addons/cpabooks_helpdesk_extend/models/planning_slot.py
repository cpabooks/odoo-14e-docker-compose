from odoo import api, models, fields, _

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    @api.onchange('company_id')
    def get_default_employee(self):
        employee = self.env['hr.employee'].search([('name','=',self.env.user.name)], limit=1)
        self.employee_id = employee.id if employee else False
        self.allocated_hours = 0.00

