from odoo import api, models, fields, _


class CRPLead(models.Model):
    _inherit = 'crm.lead'


    description = fields.One2many('crm.description.line', 'crm_lead_id', 'Internal Notes')




class CRMDescriptionLine(models.Model):
    _name = 'crm.description.line'


    crm_lead_id = fields.Many2one('crm.lead')
    desc_line = fields.Text('Descriptions')