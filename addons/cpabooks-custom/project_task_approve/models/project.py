# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError


class Project(models.Model):
    _inherit = "project.project"

    approve_task_completion = fields.Boolean(
        string="Approve Task Completion",
        default=False, copy=False,
    )

    end_stage_id = fields.Many2one(
        string="End Stage",
        comodel_name="project.task.type",
        domain="[('project_ids', 'in', id)]",
        help="Tasks in this stage are seen as done",
    )

    approver_user_id = fields.Many2one(
        string="Approver",
        comodel_name="res.users",
        help="Default approver for project tasks. This user can be redefined for each task."
    )

    @api.onchange("approve_task_completion")
    def _onchange_approve_task_completion(self):
        if self.approve_task_completion:
            self.approver_user_id = self.user_id
        else:
            self.approver_user_id = None

    @api.constrains
    def _check_approver(self):
        for project in self:
            if not project.approve_task_completion:
                if not project.approver_user_id:
                    raise ValidationError("Please set approver")
                if project.privacy_visibility == "followers" and \
                        project.approver_user_id.partner_id not in project.message_partner_ids:
                    raise ValidationError("Approver should be follower of the project")


class Task(models.Model):
    _inherit = "project.task"

    def _get_default_approver_user_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.env['project.project'].browse(project_id).approver_user_id

    approve_task_completion = fields.Boolean(
        string="Approve Task Completion",
        related="project_id.approve_task_completion",
        readonly=True,
    )

    approver_user_id = fields.Many2one(
        string="Approver",
        comodel_name="res.users",
        default=_get_default_approver_user_id
    )

    approval_state = fields.Selection(
        string='Approval State',
        selection=[('open', 'Under Approval'), ('done', 'Approved')],
        readonly=True,
    )

    is_pm = fields.Boolean(
        string="Is PM",
        compute='_compute_approval_users'
    )

    is_approver = fields.Boolean(
        string="Is Approver",
        compute='_compute_approval_users'
    )

    @api.depends('project_id', 'manager_id', 'approver_user_id')
    def _compute_approval_users(self):
        for task in self:
            task.is_pm = self.env.user == task.manager_id or self.env.user._is_admin()
            task.is_approver = self.env.user == task.approver_user_id or self.env.user._is_admin()

    @api.onchange('project_id')
    def _update_approver_onchange_project(self):
        if self.project_id:
            self.approver_user_id = self.project_id.approver_user_id

    @api.constrains('approve_task_completion', 'approver_user_id', 'approval_state')
    def _check_approver(self):
        for task in self:
            if task.approve_task_completion:
                if not task.approver_user_id:
                    raise ValidationError("Please set approver")
                if task.project_id.privacy_visibility == "followers":
                    followers = task.project_id.message_partner_ids
                    followers |= task.message_partner_ids
                    if task.approver_user_id.partner_id.id not in followers.ids:
                        raise ValidationError("Approver should be follower of the project or task")

    @api.constrains('stage_id')
    def _check_approval_stage(self):
        for task in self:
            if not task.approve_task_completion or task.stage_id != task.project_id.end_stage_id:
                continue
            if self.env.user != task.approver_user_id and not self.env.user._is_admin():
                raise UserError(u"""
                Approval required to move this task to the stage "{}"! 
                Please click the button "Send to Approve" in the task form or kanban dropdown menu.
                """.format(task.project_id.end_stage_id.name))

    def action_send_to_approve(self):
        for task in self:
            # Set the task as ready to next stage
            task.kanban_state = 'done'
            # Open approval
            task.approval_state = 'open'
            # Send request to approve completion of task to approver
            task.message_post_with_view(
                'project_task_approve.request_to_approve',
                subject=_('Task Approval: %s') % (task.name,),
                composition_mode='mass_mail',
                partner_ids=[(4, task.approver_user_id.partner_id.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def action_approve(self):
        for task in self:
            # Notify assigned user that the task has been approved
            task.message_post_with_view(
                'project_task_approve.task_approval',
                subject=_('Task Approved: %s') % (task.name,),
                composition_mode='mass_mail',
                partner_ids=[(4, task.approver_user_id.partner_id.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)
            # Move the task to end stage
            task.stage_id = task.project_id.end_stage_id
            # Set approval as done
            task.approval_state = 'done'
        if self.env.context.get('tag') == 'reload':
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return True

    def write(self, vals):
        if 'stage_id' in vals:
            # reset approval state when changing stage
            if 'approval_state' not in vals:
                vals['approval_state'] = None
        return super(Task, self).write(vals)
