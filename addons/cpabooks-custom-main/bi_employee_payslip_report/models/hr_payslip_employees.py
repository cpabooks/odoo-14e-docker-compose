from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                     required=True)
    # default = lambda self: self._get_employees_by_structure(),
    # fields.Many2many('hr.employee',
    structure_domain = fields.Many2one('hr.payroll.structure.type', string='Salary Structure Type')

    # default_employee_ids=fields.Many2many('hr.employee',

    @api.onchange('structure_domain')
    def _get_employees_by_structure(self):
        employees=[]
        if self.structure_domain:
            get_structure_type=self.env['hr.payroll.structure.type'].sudo().search([('id','=',self.structure_domain.id)])

            if get_structure_type:
                get_contracts=self.env['hr.contract'].sudo().search([('structure_type_id','in',get_structure_type.ids),('active','=','true'),('state', 'in', ('open', 'close')),('company_id', '=', self.env.company.id)])
                if get_contracts:
                    self.employee_ids=get_contracts.employee_id.ids
                    # return get_contracts.employee_id.ids
                else:
                    self.employee_ids = None
            else:
                self.employee_ids = None
        else:
            domain = [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]
            all_emp = self.env['hr.employee'].search(domain)
            self.employee_ids = all_emp.ids


