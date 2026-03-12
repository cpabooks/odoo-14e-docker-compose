# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_dedicated_food_energy(models.Model):
#     _name = 'cpabooks_dedicated_food_energy.cpabooks_dedicated_food_energy'
#     _description = 'cpabooks_dedicated_food_energy.cpabooks_dedicated_food_energy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
