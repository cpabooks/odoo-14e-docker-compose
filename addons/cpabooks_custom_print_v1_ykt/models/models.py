# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_custom__print_v1_ykt(models.Model):
#     _name = 'cpabooks_custom__print_v1_ykt.cpabooks_custom__print_v1_ykt'
#     _description = 'cpabooks_custom__print_v1_ykt.cpabooks_custom__print_v1_ykt'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
