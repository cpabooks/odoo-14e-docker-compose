# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    estimation_count = fields.Integer(compute='_compute_estimation_count', string='Number of Estimations')
    job_cost_sheet_ids = fields.One2many('job.cost.sheet', 'opportunity_id', string='Estimations')

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id')
    def _compute_sale_data(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order_ids:
                if order.state in ('draft', 'sent','sale'):
                    quotation_cnt += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.quotation_count = quotation_cnt
            lead.sale_order_count = sale_order_cnt

    def action_view_sale_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ['draft', 'sent','sale'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent','sale'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

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
