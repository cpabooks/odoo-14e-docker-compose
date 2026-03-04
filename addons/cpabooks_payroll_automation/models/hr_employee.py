from odoo import fields, models, api, _
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    structure_type_id = fields.Many2one('hr.payroll.structure.type', related='contract_id.structure_type_id',
                                        string="Salary Structure Type",
                                        readonly=True, store=True)

    def create_contract(self):
        for rec in self:
            check_existing_active_contact=self.env['hr.contract'].sudo().search([('employee_id','=',rec.id),
                                                                                      ('active','=',True),('state','=','open')])
            check_existing_contact = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.id),('active','=',True)])
            if check_existing_active_contact:
                raise ValidationError(_("An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts)"))
            else:
                if check_existing_contact:
                    get_number=len(check_existing_contact)
                else:
                    get_number=0
                get_struct_type=self.env['hr.payroll.structure.type'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1)
                if get_struct_type:
                    get_struct_type.default_struct_id=self.env['hr.payroll.structure'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1).id
                vals={
                    'name':rec.name+' Cont.'+str(get_number).zfill(2) if get_number<10 else str(get_number),
                    'structure_type_id': self.env['hr.payroll.structure.type'].sudo().search([('name','=',rec.resource_calendar_id.name)],limit=1).id,
                    'wage':0,
                    'state':'open',
                    'employee_id':rec.id,
                    'active':True,
                    'resource_calendar_id':  rec.resource_calendar_id.id
                }
                self.env['hr.contract'].sudo().create(vals)
        return True
