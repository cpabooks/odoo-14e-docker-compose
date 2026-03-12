# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_digital_signature_ptv1(models.Model):
#     _name = 'cpabooks_digital_signature_ptv1.cpabooks_digital_signature_ptv1'
#     _description = 'cpabooks_digital_signature_ptv1.cpabooks_digital_signature_ptv1'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
