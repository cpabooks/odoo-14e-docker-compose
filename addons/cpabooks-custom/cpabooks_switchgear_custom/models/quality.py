# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    project_id = fields.Many2one('project.project', string='Job Order')
