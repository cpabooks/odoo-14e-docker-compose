from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit="account.move"

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','account.move'),('company_id','=',self.env.company.id)])
        return get_signature_data

    def check_bank_detail_existency(self):
        if 'bank_detail_enable' in self.env['product.product']._fields:
            return True
        else:
            return False