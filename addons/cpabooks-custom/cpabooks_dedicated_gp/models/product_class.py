from num2words import num2words

from odoo import _, api, fields, models


class ProductClass(models.Model):
    _name = "product.class"

    name=fields.Char(string="Class")
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 domain=lambda self: [("id", '=', self.env.company.id)])



class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def class_domain(self):
        return [('company_id','=',self.env.company.id)]