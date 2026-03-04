from odoo import fields, models


class HrOvertimeLine(models.Model):
    _name = 'hr.overtime.line'

    date = fields.Date('Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    ot_type = fields.Selection([
        ('not', 'NOT'),
        ('hot', 'HOT')
    ], string='OT Type', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    number_of_hours = fields.Float(string='Number of Hours', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='draft',
        help="Overtime request.")

    def action_update_state_approved(self):
        self.write({'state': 'approved'})


