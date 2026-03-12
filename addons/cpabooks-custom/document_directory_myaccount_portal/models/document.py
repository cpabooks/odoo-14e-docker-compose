# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Document(models.Model):
    _inherit = 'documents.document'

    x_all_users = fields.Boolean(
        string="All Users",
        help="Select this checkbox to share with all Portal Users",
        related="attachment_id.x_all_users",
        readonly=False
    )

    x_partner_ids = fields.Many2many(
        'res.partner',
        string="Share on Portal",
        related="attachment_id.partner_ids",
        readonly=False
    )

    x_directory_id = fields.Many2one(
        'document.directory',
        string='Directory',
        related="attachment_id.directory_id",
        readonly=False
    )

    x_description = fields.Char(
        string="Description",
        related="attachment_id.x_description",
        help="A Description of this file. Note: This will appear on the portal",
        readonly=False
    )
