# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    enquiry_number = fields.Char(string='Enquiry Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if not vals.get('enquiry_number') or vals['enquiry_number'] == _('New'):
            vals['enquiry_number'] = self.env['ir.sequence'].next_by_code('crm.lead') or _('New')
        return super(CrmLead, self).create(vals)

    def action_new_quotation(self):
        action = super().action_new_quotation()
        action['context']['default_enquiry_number'] = self.enquiry_number
        return action
