from odoo import api, models, fields, _

class ProjectTaskScop(models.Model):
    _name = 'project.task.scope'
    _description = 'Scope For Word'
    _rec_name = 'name'

    name = fields.Char('Name')


class ProjectTaskPriority(models.Model):
    _name = 'project.task.priority'
    _description = 'Project Task Priority'
    _rec_name = 'name'

    name = fields.Char('Name')


