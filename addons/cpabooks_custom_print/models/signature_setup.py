from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class SignatureSetup(models.Model):
    _name="signature.setup"

    model=fields.Selection([('sale.order','Sale'),
                            ('purchase.order', 'Purchase'),
                            ('account.move','Invoice'),
                            ('account.payment','Payment')],string="Signature For")

    signature1=fields.Char(string="Signature 1")
    signature2=fields.Char(string="Signature 2")
    signature3=fields.Char(string="Signature 3")
    company_id=fields.Many2one('res.company',string="Company",required=True)

