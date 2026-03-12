from odoo import models, fields, api,_

class InheritHRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    type_for=fields.Selection([
        ('regular','Regular Time Off'),
        ('public_holiday','Public Holiday'),
        ('leave_with_pay','Leave With Pay'),
        ('leave_with_out_pay','Leave With Out Pay'),
    ],required=True,string="Timeoff Type For")