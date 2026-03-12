from odoo import api, models, fields, _

class ActivityTimeSheetLine(models.Model):
    _name = 'activity.timesheet.line'
    _description = 'Activity Timesheet Line'

    activity_id = fields.Many2one('mail.activity', 'Activity')
    user_id = fields.Many2one('res.users', 'User')
    date = fields.Date('Date', default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    name = fields.Text('Description', required=False, readonly=False, compute='_get_description', store=True)
    unit_amount = fields.Float('Duration')
    company_id = fields.Many2one('res.company', 'Company')

    @api.depends('activity_id')
    def _get_description(self):
        for rec in self:
            if rec.activity_id:
                rec.name = rec.activity_id.summary
            else:
                rec.name = ''

    @api.model
    def default_get(self, fields):
        """Default get value for user_id, employee_id, company_id"""
        res = super(ActivityTimeSheetLine, self).default_get(fields)
        res.update({
            'user_id': self.env.user.id if self.env.user else False,
            'employee_id': self.env.user.employee_id.id if self.env.user.employee_id else False,
            'company_id': self.env.company.id if self.env.company else False
        })
        return res

    @api.model
    def create(self, vals):
        """Create an account analytic line (Project Task timesheet) entry if activity has document_id and
        res_model_id.model == 'project.task'"""
        res = super(ActivityTimeSheetLine, self).create(vals)

        if (res.activity_id and
            res.activity_id.res_model_id.model == 'project.task' and
            res.activity_id.res_id and
            res.activity_id.document_id):
            task = res.activity_id.document_id

            # Ensure account_id is set (default to project's analytic account)
            analytic_account = task.project_id.analytic_account_id or \
                self.env['account.analytic.account'].search([], limit=1)

            if analytic_account:  # Create only if account_id is valid
                analytic_vals = {
                    'date': res.date,
                    'employee_id': res.employee_id.id,
                    'user_id': res.user_id.id,
                    'name': res.name,
                    'unit_amount': res.unit_amount,
                    'company_id': res.company_id.id,
                    'activity_id': res.activity_id.id,
                    'task_id': task.id,
                    'project_id': task.project_id.id,
                    'activity_timesheet_id': res.id,
                    'account_id': analytic_account.id,  # Ensure `account_id` is set
                }
                # Use context flag to avoid triggering reciprocal updates
                self.env['account.analytic.line'].with_context(skip_sync=True).create(analytic_vals)

        return res

    def write(self, vals):
        """Update the related project task timesheet if any changes are detected on activity timesheet."""
        # If the skip_sync flag is present, avoid doing the sync to prevent recursion.
        if self.env.context.get('skip_sync'):
            return super(ActivityTimeSheetLine, self).write(vals)

        res = super(ActivityTimeSheetLine, self).write(vals)

        fields_to_update = {'activity_id', 'user_id', 'employee_id', 'date', 'name', 'unit_amount', 'company_id'}
        if fields_to_update.intersection(vals.keys()):
            for timesheet in self:
                analytic_line = self.env['account.analytic.line'].search([
                    ('activity_id', '=', timesheet.activity_id.id),
                    ('company_id', '=', timesheet.company_id.id)
                ], limit=1)

                if analytic_line:
                    analytic_vals = {
                        'date': timesheet.date,
                        'employee_id': timesheet.employee_id.id,
                        'user_id': timesheet.user_id.id,
                        'name': timesheet.name,
                        'unit_amount': timesheet.unit_amount,
                        'company_id': timesheet.company_id.id
                    }
                    # Use the context flag to prevent recursive updates.
                    analytic_line.with_context(skip_sync=True).write(analytic_vals)

        return res

    def unlink(self):
        """Delete the related project task timesheet if the activity timesheet is deleted."""
        # If the skip_sync flag is present, avoid syncing to prevent recursion.
        if self.env.context.get('skip_sync'):
            return super(ActivityTimeSheetLine, self).unlink()

        for timesheet in self:
            analytic_line = self.env['account.analytic.line'].search([
                ('activity_timesheet_id', '=', timesheet.id),
                ('company_id', '=', timesheet.company_id.id)
            ], limit=1)
            if analytic_line:
                analytic_line.with_context(skip_sync=True).unlink()

        return super(ActivityTimeSheetLine, self).unlink()
