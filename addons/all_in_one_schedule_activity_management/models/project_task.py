from signal import valid_signals

from odoo import api, models, fields, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_launch_activity_create_wizard(self):
        for rec in self:
            return {
                'name': _('Create Activity'),
                'type': 'ir.actions.act_window',
                'res_model': 'activity.create.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_task_id': rec.id
                }
            }

    def _compute_activity_count(self):
        for rec in self:
            activity_ids_count = self.env['mail.activity'].search_count([
                ('res_id', '=', rec.id),
                ('res_model_id.model', '=', 'project.task')
            ])
            rec.activity_count = activity_ids_count if activity_ids_count >= 1 else 0


    activity_count = fields.Integer('Total Activities', compute=_compute_activity_count, default=0)
    activity_planned_hours = fields.Float('Total Activity Planned Hours', compute='_compute_total_planned_hours')

    def _compute_total_planned_hours(self):
        for rec in self:
            all_activities = self.env['mail.activity'].search([('document_id', '=', rec.id)])
            total_time = sum([act.initial_planned_hour for act in all_activities])
            rec.activity_planned_hours = total_time

    def action_activity(self):
        return {
            'name': f'Activities of {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_mode': 'tree,form',
            'domain': [('res_id', '=', self.id), ('res_model_id.model', '=', 'project.task')],# Ensures only relevant activities are shown
        }


class ProjectTaskAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    activity_id = fields.Many2one('mail.activity', 'Activity')
    activity_timesheet_id = fields.Many2one('activity.timesheet.line', 'Activity Timesheet')


    def write(self, vals):
        res = super(ProjectTaskAccountAnalyticLine, self).write(vals)
        if any(field in vals for field in ['name', 'date', 'employee_id', 'unit_amount']) and self.activity_id and self.activity_timesheet_id:
            analytic_vals = {
                'date': vals.get('date', self.date),
                'name': vals.get('name', self.name),
                'employee_id': vals.get('employee_id', self.employee_id),
                'unit_amount': vals.get('unit_amount', self.unit_amount)
            }
            activity_timesheet = self.env['activity.timesheet.line'].search([
                ('id', '=', self.activity_timesheet_id.id),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            if activity_timesheet:
                activity_timesheet.write(analytic_vals)
        return res

    def unlink(self):
        """Delete the related project task timesheet if the activity timesheet is deleted."""

        # If the skip_sync flag is present, avoid syncing to prevent recursion.
        # if self.env.context.get('skip_sync'):
        #     return super(ProjectTaskAccountAnalyticLine, self).unlink()

        for rec in self:
            if rec.activity_timesheet_id:
                activity_timesheet = self.env['activity.timesheet.line'].sudo().search([
                    ('id', '=', rec.activity_timesheet_id.id),
                    ('company_id', '=', rec.company_id.id)
                ], limit=1)

                # Ensure the record still exists before trying to unlink it
                if activity_timesheet.exists():
                    activity_timesheet.unlink()

        # Ensure the record still exists before unlinking
        existing_records = self.filtered(lambda r: r.exists())
        return super(ProjectTaskAccountAnalyticLine, existing_records).unlink()

