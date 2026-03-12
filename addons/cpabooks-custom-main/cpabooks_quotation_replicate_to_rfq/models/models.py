# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_quotation_replicate_to_rfq(models.Model):
#     _name = 'cpabooks_quotation_replicate_to_rfq.cpabooks_quotation_replicate_to_rfq'
#     _description = 'cpabooks_quotation_replicate_to_rfq.cpabooks_quotation_replicate_to_rfq'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
