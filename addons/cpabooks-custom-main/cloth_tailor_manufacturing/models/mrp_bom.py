# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def custom_action_view_cloth_requests(self):
        action = self.env.ref('cloth_tailor_management_odoo.action_cloth_request_details').read()[0]
        action['context'] = {}
        cloth_request_ids = self.env['cloth.request.details'].search([('custom_bom_id', 'in', self.ids)])
        action['domain'] = [('id', 'in', cloth_request_ids.ids)]
        return action