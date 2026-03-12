# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_chart_of_account_v1(models.Model):
#     _name = 'cpabooks_chart_of_account_v1.cpabooks_chart_of_account_v1'
#     _description = 'cpabooks_chart_of_account_v1.cpabooks_chart_of_account_v1'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
