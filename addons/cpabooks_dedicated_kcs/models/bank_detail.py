from odoo import fields, models, api


class BankDetails(models.Model):
    _name = 'bank.details'
    _rec_name = 'bank_name'

    bank_name = fields.Char(string="Bank Name")
    bank_account_number = fields.Char(string="Bank Account Number")
    bank_iban_number = fields.Char(string="IBAN Number")
    bank_address = fields.Char(string="Bank Address")
    bank_branch = fields.Char(string="Bank Branch")
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 domain=lambda self: [("id", '=', self.env.company.id)],default=lambda self:self.env.company.id)


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def bank_domain(self):
        return [('company_id','=',self.env.company.id)]