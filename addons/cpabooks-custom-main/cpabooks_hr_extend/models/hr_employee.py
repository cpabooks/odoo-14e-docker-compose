from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    eid_no = fields.Char('EID No', groups="hr.group_hr_user", tracking=True)
    work_permit_expire = fields.Date('Work Permit Expire Date', groups="hr.group_hr_user", tracking=True)
