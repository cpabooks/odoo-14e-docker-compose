# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabook_accounting_automation(models.Model):
#     _name = 'cpabook_accounting_automation.cpabook_accounting_automation'
#     _description = 'cpabook_accounting_automation.cpabook_accounting_automation'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
