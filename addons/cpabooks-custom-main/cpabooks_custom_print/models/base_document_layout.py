# -*- coding: utf-8 -*-

from odoo import models, fields, _


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    header_logo = fields.Image(related='company_id.header_logo', readonly=True)
    partner_logo = fields.Image(related='company_id.partner_logo', readonly=True)
    footer_text = fields.Char(related='company_id.footer_text', readonly=True)
