# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    calendar_meeting_ids = fields.Many2many(
        "calendar.event", string='Meeting Ids', readonly=True, compute='_compute_get_meeting_ids')
    sale_quotation_ids = fields.Many2many(
        "sale.order", string="Quotation Ids", readonly=True, compute='_compute_get_quotation_ids')

    def _compute_get_meeting_ids(self):
        if self:
            for data in self:
                meeting_details = data.env['calendar.event'].search(
                    [('opportunity_id', 'in', data.ids)])
                if (meeting_details, False):
                    vals_meeting_ids = []

                    for rec in meeting_details:
                        vals_meeting_ids.append(rec.id)

                    data.calendar_meeting_ids = vals_meeting_ids

    def _compute_get_quotation_ids(self):
        if self:
            for data in self:
                quotation_details = data.env['sale.order'].search(
                    [('opportunity_id', 'in', data.ids)])
                if (quotation_details, False):
                    vals_quotation_ids = []

                    for rec in quotation_details:
                        vals_quotation_ids.append(rec.id)

                    data.sale_quotation_ids = vals_quotation_ids
