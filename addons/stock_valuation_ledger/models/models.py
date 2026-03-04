# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class stock_valuation_ledger(models.Model):
#     _name = 'stock_valuation_ledger.stock_valuation_ledger'
#     _description = 'stock_valuation_ledger.stock_valuation_ledger'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
