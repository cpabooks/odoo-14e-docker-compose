from odoo import fields, models


class ProjectDefaultTask(models.Model):
    _name = 'project.default.task'

    name = fields.Char(string="Name", required=True)
    parent_id = fields.Many2one('project.default.task', string='Parent Task', domain=[('parent_id', '=', False)])
