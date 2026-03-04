# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_dedicated_gp(models.Model):
#     _name = 'cpabooks_dedicated_gp.cpabooks_dedicated_gp'
#     _description = 'cpabooks_dedicated_gp.cpabooks_dedicated_gp'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
