from odoo import api, models, fields, _

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    status = fields.Selection(
        [
            ('pending','Pending'),
            ('in_progress','In-Progress'),
            ('done','Done'),
            ('plan','Plan'),
        ], 'Status', default='pending'
    )

    @api.onchange('company_id')
    def get_default_employee(self):
        employee = self.env['hr.employee'].search([('name','=',self.env.user.name)], limit=1)
        self.employee_id = employee.id if employee else False
        self.allocated_hours = 0.00


    @api.onchange('employee_id')
    def get_role_id(self):
        for rec in self:
            if rec.employee_id:
                rec.role_id = rec.employee_id.default_planning_role_id.id or False


