from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TimesheetTemplate(models.Model):
    _name = 'timesheet.template.config'

    name = fields.Char(string='Template Name')
    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Tasks", domain="[('project_id','=',project_id)]")
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.company.id)
    is_active = fields.Boolean(string="Is Active", default=True)

    timesheet_line = fields.One2many('timesheet.template.config.line', 'template_id', string="Timesheet Line")
    date = fields.Date('Date', default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('added', 'Added into timesheet')], default="draft", readonly=True)

    @api.model
    def create(self, vals):
        res = super(TimesheetTemplate, self).create(vals)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('sequence_for_timesheet_template')
        return res

    def write(self, vals):
        res = super(TimesheetTemplate, self).write(vals)
        if res and vals.get('date', ''):
            self.state = 'draft'
        return res

    @api.onchange('project_id')
    def assign_line_data(self):
        val_list = []
        # First, unlink the existing lines
        self.timesheet_line = False
        # Create new lines based on the project's employee_line
        for rec in self.project_id.employee_line:
            vals = (0, 0, {
                'employee_id': rec.employee_id.id,
                'project': self.project_id.id
            })
            val_list.append(vals)

        # Now assign the new values to the timesheet_line field
        self.timesheet_line = val_list

    def add_into_timesheet(self):
        if not self.timesheet_line:
            raise ValidationError(_('No Item available on Timesheet line!'))

        vals_lst = []
        existing_users = []
        timesheet = self.env['account.analytic.line']

        for rec in self.timesheet_line:
            if not rec.project.analytic_account_id:
                raise ValidationError(
                    _('The project "%s" does not have an analytic account. Please configure it.') % rec.project.name)

            vals = {
                'name': rec.description,
                'date': rec.template_id.date,
                'unit_amount': rec.unit_amount,
                'account_id': rec.project.analytic_account_id.id,  # Ensure it's always set
                'user_id': rec.employee_id.user_id.id if rec.employee_id.user_id else False,
                'company_id': rec.template_id.company_id.id,
                'currency_id': rec.template_id.company_id.currency_id.id,
                'task_id': rec.task.id,
                'so_line': rec.task.sale_line_id.id,
                'project_id': rec.project.id,
                'employee_id': rec.employee_id.id,
                'department_id': rec.employee_id.department_id.id,
                'validated': False
            }
            vals_lst.append(vals)

            # Check for existing timesheets for the same user and date
            if rec.employee_id.user_id:
                exist = timesheet.search([
                    ('date', '=', rec.template_id.date),
                    ('user_id', '=', rec.employee_id.user_id.id)
                ], limit=1)

                if exist and rec.employee_id.user_id.name:
                    existing_users.append(rec.employee_id.user_id.name)

        # Ensure existing_users contains only valid strings
        existing_users = [user for user in existing_users if isinstance(user, str)]

        # Create timesheets if no existing users have timesheets for the date
        if existing_users:
            message = f"Timesheet already available for: {', '.join(existing_users)}"
        else:
            timesheet.create(vals_lst)
            self.state = 'added'
            message = f'Timesheet created successfully for date: {self.date}'

        # Create a result record and show the message to the user
        result_id = self.env['timesheet.templates.config.result'].create({
            'message': message
        })
        return {
            'name': 'Message',
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.templates.config.result',
            'view_mode': 'form',
            'view_id': self.env.ref('bi_employee_payslip_report.timehseet_templates_config_result_form_view').id,
            'target': 'new',
            'res_id': result_id.id,
        }

class TimesheetTemplateLine(models.Model):
    _name = 'timesheet.template.config.line'


    template_id = fields.Many2one('timesheet.template.config')
    project = fields.Many2one('project.project', 'Project', store=True, required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    task = fields.Many2one('project.task', string="Task", domain="[('project_id','=',project)]")
    description = fields.Char(string="Description", default="Timesheet Adjustment")
    unit_amount = fields.Float(string="Duration", default=8)
