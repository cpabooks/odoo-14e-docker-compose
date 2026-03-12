# -*- coding: utf-8 -*-

from odoo import fields, models, api


class JobCostSheet(models.Model):
    _inherit = 'job.cost.sheet'

    enquiry_number = fields.Char(string='Enquiry Number')
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', domain="[('type', '=', 'opportunity')]")
    quotation_count = fields.Integer(compute='_compute_quotation_count', string='Number of Quotations')
    order_ids = fields.One2many('sale.order', 'job_cost_sheet_id', string='Orders')

    @api.depends('order_ids')
    def _compute_quotation_count(self):
        for job in self:
            job.quotation_count = len(job.order_ids.filtered(lambda l: l.state in ('draft', 'sent')))

    def button_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("cpabooks_job_order_extend.action_new_quotation")
        action['context'] = {
            'search_default_job_cost_sheet_id': self.id,
            'default_job_cost_sheet_id': self.id,
        }
        return action

    def action_view_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'default_job_cost_sheet_id': self.id
        }
        action['domain'] = [('job_cost_sheet_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action
