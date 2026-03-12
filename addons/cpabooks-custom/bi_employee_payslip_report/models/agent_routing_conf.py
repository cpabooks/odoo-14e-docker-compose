from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class SignatureSetup(models.Model):
    _name="agent.routing"
    _rec_name = "code"

    _sql_constraints = [
        ('code_company_uniq', 'unique(code,company_id)', 'Already exists for this company!')
    ]

    code=fields.Char(string="Routing Code")
    company_id=fields.Many2one('res.company',string="Company",required=True,domain=lambda self:[("id",'=',self.env.company.id)])


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def code_domain(self):
        return [('company_id','=',self.env.company.id)]
