# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cost_estimate_customer_ld_v1fm(models.Model):
#     _name = 'cost_estimate_customer_ld_v1fm.cost_estimate_customer_ld_v1fm'
#     _description = 'cost_estimate_customer_ld_v1fm.cost_estimate_customer_ld_v1fm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
