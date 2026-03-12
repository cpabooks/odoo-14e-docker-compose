# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_project_issue_note(models.Model):
#     _name = 'cpabooks_project_issue_note.cpabooks_project_issue_note'
#     _description = 'cpabooks_project_issue_note.cpabooks_project_issue_note'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
