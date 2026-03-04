from odoo import api, models, fields, _

class ProjectProject(models.Model):
    _inherit = 'project.project'

    employee_line = fields.One2many('project.employee.line', 'project_id', 'Employees')


class ProjectEmployeeLine(models.Model):
    _name = 'project.employee.line'
    _description = 'Project Employee Line'

    project_id = fields.Many2one('project.project', 'Project')
    employee_id = fields.Many2one('hr.employee', 'Employee')
