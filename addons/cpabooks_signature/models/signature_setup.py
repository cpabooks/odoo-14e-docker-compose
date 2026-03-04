from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class SignatureSetup(models.Model):
    _name="signature.setup"

    _sql_constraints = [
        ('model_company_uniq', 'unique(model,company_id)', 'Already exists for this company!')
    ]
    model = fields.Selection([('sale.order', 'Sale'),
                              ('purchase.order', 'Purchase'),
                              ('account.move', 'Invoice'),
                              ('account.payment', 'Payment'),
                              ('stock.picking', 'Delivery Order'),
                              ('hr.payslip', 'Employee Payslip'),
                              ('quotation.job.order', 'Job Order'),
                              ('mrp.bom', 'MRP BoM')], string="Signature For")

    signature1=fields.Char(string="Signature 1")
    signature2=fields.Char(string="Signature 2")
    signature3=fields.Char(string="Signature 3")
    company_id=fields.Many2one('res.company',string="Company",required=True,domain=lambda self:[("id",'=',self.env.company.id)])
    
    # @api.model
    # def create(self, vals_list):
    #     if 'model' in vals_list:
    #         get_existing=self.env['signature.setup'].search([('model','=',vals_list['model']),('company_id','=',self.env.company.id)])
    #         if get_existing:
    #             raise ValidationError(_("Already exists for comapny:"+"'"+self.env.company.name+"'"))
    #         else:
    #             return super(SignatureSetup, self).create(vals_list)
    #
    # def write(self, vals):
    #     if 'model' in vals:
    #         get_existing = self.env['signature.setup'].search(
    #             [('model', '=', vals['model']), ('company_id', '=', self.env.company.id)])
    #         if get_existing:
    #             raise ValidationError(_("Already exists for comapny:"+"'"+self.env.company.name+"'"))
    #         else:
    #             return super(SignatureSetup, self).write(vals)







class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def signature_domain(self):
        return [('company_id','=',self.env.company.id)]

