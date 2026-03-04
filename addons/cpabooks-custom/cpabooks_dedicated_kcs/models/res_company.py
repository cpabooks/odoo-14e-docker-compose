from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    bank_details=fields.Many2many('bank.details',string="Bank Details",domain="[('id','in',demo_bank_details)]")

    demo_bank_details=fields.Many2many('bank.details',compute="_get_bank_details")


    def _get_bank_details(self):
        for rec in self:
            rec.demo_bank_details=self.env['bank.details'].sudo().search([('company_id','=',rec.id)]).ids