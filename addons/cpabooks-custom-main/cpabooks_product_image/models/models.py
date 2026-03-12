# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bt_upload_image_in_quotation_line(models.Model):
#     _name = 'bt_upload_image_in_quotation_line.bt_upload_image_in_quotation_line'
#     _description = 'bt_upload_image_in_quotation_line.bt_upload_image_in_quotation_line'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
