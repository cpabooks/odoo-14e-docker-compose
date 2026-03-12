# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cpabooks_delivery_status_on_sales_order(models.Model):
#     _name = 'cpabooks_delivery_status_on_sales_order.cpabooks_delivery_status_on_sales_order'
#     _description = 'cpabooks_delivery_status_on_sales_order.cpabooks_delivery_status_on_sales_order'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
