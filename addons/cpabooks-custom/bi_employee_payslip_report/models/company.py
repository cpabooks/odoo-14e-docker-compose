from odoo import models, fields, api


class CompanyExtend(models.Model):
    _inherit = 'res.company'

    company_mol_id=fields.Char(string="Company MOL ID")