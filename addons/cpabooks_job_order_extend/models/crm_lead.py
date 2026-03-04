# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    estimation_count = fields.Integer(compute='_compute_estimation_count', string='Number of Estimations')
    job_cost_sheet_ids = fields.One2many('job.cost.sheet', 'opportunity_id', string='Estimations')

    @api.depends('job_cost_sheet_ids')
    def _compute_estimation_count(self):
        for lead in self:
            lead.estimation_count = len(lead.job_cost_sheet_ids)

    def button_new_estimation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("cpabooks_job_order_extend.action_new_estimation")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'default_enquiry_number': self.enquiry_number,
        }
        return action

    def action_view_estimation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("bi_odoo_job_costing_management.action_job_cost_sheet")
        action['context'] = {
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id)]
        job_cost_sheet = self.mapped('job_cost_sheet_ids')
        if len(job_cost_sheet) == 1:
            action['views'] = [(self.env.ref('bi_odoo_job_costing_management.job_cost_sheet_form_view').id, 'form')]
            action['res_id'] = job_cost_sheet.id
        return action
