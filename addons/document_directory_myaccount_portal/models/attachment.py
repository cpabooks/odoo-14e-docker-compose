# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    partner_ids = fields.Many2many(
        'res.partner',
        string="Share on Portal"
    )

    x_all_users = fields.Boolean(
        string="All Users",
        help="Select this checkbox to share with all Portal Users"
    )

    x_description = fields.Char(
        string="Description",
        help="A Description of this file. Note: This will appear on the portal"
    )
