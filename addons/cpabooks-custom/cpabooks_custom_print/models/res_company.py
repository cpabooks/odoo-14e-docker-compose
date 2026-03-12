# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    header_logo = fields.Image(string='Header Logo (Size 1280px x 200px)')
    partner_logo = fields.Image(string='Footer Logo (Size 1280px x 80px)')
    footer_text = fields.Char(string='Footer Text')
