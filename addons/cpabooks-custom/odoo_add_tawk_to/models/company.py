# -*- coding: utf-8 -*-

from odoo import api, fields, models

class res_company(models.Model):
    _inherit = "res.company"

    tawk_id = fields.Char(string='Tawk.to Site ID')




