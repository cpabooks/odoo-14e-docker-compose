
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal



class CrmLead(models.Model):
    _inherit = 'crm.lead'

    multi_salesman = fields.Many2many('res.users', string="Salesman", default=lambda self: self.env.user.ids)
    multi_sales_team = fields.Many2many('crm.team', string="Sales Team",
                                        default=lambda self: self.env.user.sale_team_id.ids)

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_team_id': self.team_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)],
            'default_multi_salesman':[(6,0,self.multi_salesman.ids)],
            'default_multi_sales_team':[(6,0,self.multi_sales_team.ids)]
        }
        return action
