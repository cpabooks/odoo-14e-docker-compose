from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = 'id asc'

    task_seq = fields.Float(string='Sequence', default=0.00)
    total_job=fields.Float(string='Total Job %')
    complete_job=fields.Float(string='Completed')
    balance_job=fields.Float(string='Balance')
    task_type=fields.Selection([('main','Main Task'),('sub','Sub Task')],string="Task Type")

    def write(self, vals):
        for rec in self:
            if rec.task_parent_id and 'complete_job' in vals:
                total_complete_job = vals['complete_job']
                # avg_complete_job = 0
                for subtask in rec.task_parent_id.subtask_ids-self:
                    total_complete_job += subtask.complete_job


                total_sub_task_complete_job = round(total_complete_job, 2)
                rec.parent_id.complete_job = total_sub_task_complete_job
                rec.parent_id.balance_job=rec.parent_id.total_job-total_sub_task_complete_job
                super(ProjectTask, self).write(vals)
            elif rec.subtask_ids and 'total_job' in vals:
                sub_task_count=len(rec.subtask_ids)
                dividation_value=vals['total_job']/sub_task_count
                for sub_task in rec.subtask_ids:
                    sub_task.total_job=dividation_value
                super(ProjectTask, self).write(vals)
            else:
                super(ProjectTask, self).write(vals)

    @api.onchange('complete_job')
    def _job_percentage(self):
        for rec in self:
            # rec.complete_job=rec.total_job-rec.balance_job
            if rec.total_job<rec.complete_job:
                raise ValidationError(_("Completed job must be equal or smaller then total job(%)"))
            else:
                rec.balance_job=rec.total_job-rec.complete_job

    @api.onchange('total_job')
    def _onchange_total_job(self):
        for rec in self:
            # rec.complete_job=rec.total_job-rec.balance_job
            if rec.total_job < rec.complete_job:
                raise ValidationError(_("Total job must be greater then Completed job"))
            else:
                rec.balance_job = rec.total_job - rec.complete_job

    def action_subtask(self):
        self.ensure_one()
        return {
            'name': 'Sub-tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'domain': [('task_parent_id', '=', self.id)],
        }
