from odoo import api, models, fields, _


class CPAIssue(models.Model):
    _name = 'cpa.issue'
    _description = 'Issue List'

    name = fields.Char(string='Issue Title', required=True)