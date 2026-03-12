# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_site_report(models.Model):
#     _name = 'cpabooks_site_report.cpabooks_site_report'
#     _description = 'cpabooks_site_report.cpabooks_site_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
