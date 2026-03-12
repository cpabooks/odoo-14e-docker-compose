from odoo import models, fields, api

class SaaSClient(models.Model):
    _inherit ='saas.client'

    db_template = fields.Char(string='DB Template', related='saas_contract_id.db_template', readonly=True)
    active = fields.Boolean('Active', default=True, copy=True)
