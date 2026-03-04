# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_bank_details_pt(models.Model):
#     _name = 'cpabooks_bank_details_pt.cpabooks_bank_details_pt'
#     _description = 'cpabooks_bank_details_pt.cpabooks_bank_details_pt'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
