from odoo import fields, models, api
class HRPayslipInherit(models.Model):
    _inherit = "hr.payslip"


    def get_signature(self):
        get_model=self.env['ir.model'].sudo().search([('model','=','signature.setup')])
        if get_model:
            get_signature_data=self.env['signature.setup'].search([('model','=','hr.payslip'),('company_id','=',self.env.company.id)])
            return  get_signature_data
        else:
            return []