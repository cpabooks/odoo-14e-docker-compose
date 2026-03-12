# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_custom_updates(models.Model):
#     _name = 'cpabooks_custom_updates.cpabooks_custom_updates'
#     _description = 'cpabooks_custom_updates.cpabooks_custom_updates'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
