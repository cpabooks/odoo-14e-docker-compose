# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string='Estimation')
    is_technical_submittal = fields.Boolean(string='Technical Submittal')
    ts_project = fields.Char(string='Project')
    ts_location = fields.Char(string='Location')
    ts_owner = fields.Char(string='Owner')
    ts_project_mgmt = fields.Char(string='Project Management')
    ts_consultant = fields.Char(string='Consultant')
    ts_mep_consultant = fields.Char(string='MEP Consultant')
    ts_main_consultant = fields.Char(string='Main Consultant')
    ts_mep_contractor = fields.Char(string='MEP Contractor')
    ts_designed_panels = fields.Char(string='Designed Panels')
    ts_reference_no = fields.Char(string='Reference No.')
