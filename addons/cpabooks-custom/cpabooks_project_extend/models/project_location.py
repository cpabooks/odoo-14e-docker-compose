from odoo import api, models, fields, _

class ProjectLocation(models.Model):
    _name = 'project.location'
    _description = 'Project Location'

    name = fields.Char('Name')