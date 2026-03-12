from odoo import api, models, fields, _

class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def add_users_on_show_task_employee(self):
        group_id = self.search([('name', '=', 'Show tasks on employee')])
        employee_ids = self.env['hr.employee'].search([])
        user_ids = []
        for employee in employee_ids:
            user_id = self.env['res.users'].search([('id', '=', employee.user_id.id)], limit=1)
            if user_id:
                user_ids.append(user_id.id)

        group_id.write({
            'users': [(6, 0, user_ids)]
        })
