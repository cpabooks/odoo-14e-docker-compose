from odoo import fields, models


class hrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False, required=False,
                                 company_dependent=True,
                                 default=lambda self: self.env['account.journal'].sudo().search([
                                     ('type', '=', 'general'),('name','=','Salary Journal') ,('company_id', '=', self.env.company.id)], limit=1))


