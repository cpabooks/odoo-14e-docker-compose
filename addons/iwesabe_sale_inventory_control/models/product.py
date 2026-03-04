# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_negative_stock  = fields.Boolean('Allow Negative Stock', copy=False)
    
