from odoo import models, fields, api, modules, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SignatureSetup(models.Model):
    _name = "signature.setup"

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

    signature1 = fields.Char(string="Signature 1")
    signature2 = fields.Char(string="Signature 2")
    signature3 = fields.Char(string="Signature 3")
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 domain=lambda self: [("id", '=', self.env.company.id)])

    def create_default_signature_setup(self):
        models = {
            'sale.order': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'purchase.order': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'account.move': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'account.payment': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'stock.picking': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'hr.payslip': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'quotation.job.order': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            },
            'mrp.bom': {
                'signature1': 'Prepared By',
                'signature2': '',
                'signature3': 'Approved By',
            }
        }

        for model, val in models.items():
            try:
                # Check if the record exists
                existence = self.env['signature.setup'].search([
                    ('company_id', '=', self.env.company.id),
                    ('model', '=', model)
                ], limit=1)

                # Create the record if it does not exist
                if not existence:
                    vals = {
                        'model': model,
                        'company_id': self.env.company.id,
                        'signature1': val.get('signature1', ''),
                        'signature2': val.get('signature2', ''),
                        'signature3': val.get('signature3', ''),
                    }
                    self.env['signature.setup'].create(vals)
            except Exception as e:
                # Log the error and rollback the transaction
                _logger.error(
                    f"Error creating signature setup for model '{model}' in company '{self.env.company.display_name}': {str(e)}")
                self.env.cr.rollback()

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

    user_signature = fields.Binary(string="Signature")
    # user_signature_name = fields.Char()

    user_stamp = fields.Binary(string="Stamp")

    # is_admin_user = fields.Boolean(string='Is Admin', default=False)
    # user_stamp_name = fields.Char()
    def signature_domain(self):
        return [('company_id', '=', self.env.company.id)]

    #
    # @api.onchange('company_id')
    # def get_default_admin(self):
    #     get_admin_power_group = self.env['res.groups'].sudo().search([('name', '=ilike', 'Admin Power')])
    #     uid = self.env.uid
    #     admin = []
    #     for i in get_admin_power_group.users.ids:
    #         if uid == i:
    #             admin.append(i)
    #     if uid in admin:
    #         self.is_admin_user = True
