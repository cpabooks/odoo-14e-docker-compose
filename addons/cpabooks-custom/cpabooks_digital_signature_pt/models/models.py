# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class digital_signature_ps(models.Model):
#     _name = 'digital_signature_ps.digital_signature_ps'
#     _description = 'digital_signature_ps.digital_signature_ps'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
