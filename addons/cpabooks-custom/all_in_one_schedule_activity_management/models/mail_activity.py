# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from collections import defaultdict
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.populate import compute


class MailActivity(models.Model):
    """This class is used to inherit the mail.activity model"""

    _inherit = "mail.activity"

    seq = fields.Char('Name', readonly=True)
    task_id = fields.Many2one('project.task', 'Select Task')
    sub_task_id = fields.Many2one('project.task', 'Sub Task')
    initial_planned_hour = fields.Float('Initial Planned Hours', default=0.5)
    total_spent_time = fields.Float('Total Spent Time')
    project_id = fields.Many2one('project.project', 'Project')
    company_id = fields.Many2one('res.company', 'Company')
    issue_id = fields.Many2one('cpa.issue', 'Issue')

    @api.model
    def action_update_company_id(self):
        for rec in self:
            if rec.task_id:
                rec.company_id =  rec.task_id.company_id.id

    @api.model
    def default_get(self, vals):
        res = super().default_get(vals)
        res.update({
            'company_id': self.env.company.id
        })
        return res

    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        if self.activity_type_id:
            if self.activity_type_id.summary:
                self.summary = self.activity_type_id.summary
            if not self.date_deadline:
                self.date_deadline = self._calculate_date_deadline(self.activity_type_id)
            if self.activity_type_id.default_user_id:
                self.user_id = self.activity_type_id.default_user_id
            elif not self.activity_type_id.default_user_id and not self.user_id:
                self.user_id = self.env.user
            if self.activity_type_id.default_description:
                self.note = self.activity_type_id.default_description

    @api.onchange('project_id')
    def _action_update_task(self):
        self.task_id = False

    @api.onchange('task_id')
    def get_customer(self):
        if self.task_id and self.task_id.partner_id:
            self.partner_id = self.task_id.partner_id.id
        else:
            self.partner_id = False

    @api.model
    def default_get(self, fields_list):
        res = super(MailActivity, self).default_get(fields_list)
        project_task_model = self.env['ir.model'].sudo().search([
            ('model', '=', 'project.task')
        ], limit=1)
        if project_task_model:
            res.update({
                'res_model_id': project_task_model.id,
            })
        return res

    @api.onchange('task_id')
    def get_task_val(self):
        self.ensure_one()
        self.res_name = self.task_id.name if self.task_id else ''
        self.document_id = self.task_id.id if self.task_id else False

    def _get_project_mail_activity(self):
        for rec in self:
            if rec.document_id and rec.res_id and rec.res_model_id.model == 'project.task':
                rec.project_id = rec.document_id.project_id.id if rec.document_id.project_id else False

    @api.model
    def action_get_project_mail_activity(self):
        """Get project for every activity"""
        activities = self.sudo().search([
            ('res_model_id.model', '=', 'project.task'),
            ('document_id', '=', True),
            ('project_id', '=', False)
        ])
        activities._get_project_mail_activity()

    @api.model
    def create(self, vals_list):
        # Handle single record creation (Odoo 14+ supports batch creation)
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            # Set res_id from task_id if provided
            if vals.get('task_id') and not vals.get('res_id'):
                task = self.env['project.task'].browse(vals['task_id'])
                if task.exists():
                    vals.update({
                        'res_model': 'project.task',  # Must set BOTH fields
                        'res_id': task.id
                    })

            # Handle sequence
            if not vals.get('seq'):
                sequence = self.env['ir.sequence'].next_by_code('activity.sequence')
                vals['seq'] = sequence if sequence else 'DRAFT'
                
        res = super(MailActivity, self).create(vals_list)

        summary = f"{res.issue_id.name if res.issue_id else ''} {res.res_name[:13]} {res.summary}"
        res.summary = summary.strip()

        if res.res_id and res.res_model_id.model ==  'project.task':
            res.task_id = res.res_id
        res._get_project_mail_activity()
        res.action_task_status()
        if len(res.timesheet_ids) == 0:
            print('No Time Sheet')
        if not res.timesheet_ids:
            res.add_timesheet_ids()
        return res

    def add_timesheet_ids(self):
        timesheet_vals = {
            'user_id': self.user_id.id,
            'activity_id': self.id,
            'date': date.today(),
            'employee_id': self.user_id.employee_id.id,
            'name': self.summary,
            'unit_amount': 0.5,
            'company_id': self.env.company.id
        }
        self.env['activity.timesheet.line'].sudo().create(timesheet_vals)

    def write(self, vals):
        for rec in self:
            rec_vals = vals.copy()

            if rec_vals.get('res_name') and not rec_vals.get('summary', rec.summary):
                rec_vals['summary'] = rec_vals['res_name'][:13]

            elif not rec_vals.get('res_name') and rec.res_name and not rec.summary:
                rec_vals['summary'] = rec.res_name[:13]

            if rec_vals.get('state'):
                self.action_task_status()

            super(MailActivity, rec).write(rec_vals)

        return True

    def reset_date(self):
        for rec in self:
            print(rec.date_deadline, date.today())
            if rec.date_deadline < date.today():
                rec.date_deadline = date.today()

    def _compute_document_relation(self):
        for rec in self:
            if rec.res_model_id.model == 'project.task' and rec.res_id:
                task = self.env['project.task'].search([('id', '=', rec.res_id)], limit=1)
                rec.document_id = task.id
            else:
                rec.document_id = False

    document_id = fields.Many2one('project.task', 'Document Relation', compute=_compute_document_relation)
    state = fields.Selection(
        [
            ("overdue", "Overdue"),
            ("today", "Today"),
            ("planned", "Planned"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        compute="_compute_state",
        store=True,
        help="state for the activity",
    )
    active = fields.Boolean("Active", default=True,
                            help="The record make Active")
    activity_type = fields.Many2many(
        "activity.tag", string="Activity Type",
        help="Activity type"
    )
    activity_done_feedback = fields.Text('Feedback')
    partner_id = fields.Many2one('res.partner', 'Customer')
    timesheet_ids = fields.One2many('activity.timesheet.line', 'activity_id', 'Time Sheet')
    aging_days = fields.Integer('Aging Days', compute="_compute_aging_days")

    @api.depends('create_date')
    def _compute_aging_days(self):
        today = date.today()
        for rec in self:
            if rec.create_date:
                create_date_only = rec.create_date.date()
                delta = today - create_date_only
                rec.aging_days = delta.days
            else:
                rec.aging_days = 0


    def action_mail_on_due_date(self):
        """This function is used to send mails on due date"""
        activity_email = self.env["mail.activity"].search([])
        notification_on_date = (
            self.env["ir.config_parameter"].sudo().get_param("notify_on_due_date")
        )
        notification_on_expiry = (
            self.env["ir.config_parameter"].sudo().get_param("notify_on_expiry")
        )
        for rec in activity_email:
            if notification_on_expiry:
                if rec.date_deadline < date.today():
                    self.env["mail.mail"].sudo().create(
                        {
                            "email_from": self.env.company.email,
                            "author_id": self.env.user.partner_id.id,
                            "body_html": "Hello <br> You missed the %s activity for the document %s </br>"
                                         % (rec.activity_type_id.name, rec.res_name),
                            "subject": "%s Activity missed" % rec.activity_type_id.name,
                            "email_to": rec.user_id.email,
                        }
                    ).send(auto_commit=False)
            if notification_on_date:
                if rec.date_deadline == date.today():
                    self.env["mail.mail"].sudo().create(
                        {
                            "email_from": self.env.company.email,
                            "author_id": self.env.user.partner_id.id,
                            "body_html": "Hello <br> Today is your %s activity for the document %s </br>"
                                         % (rec.activity_type_id.name, rec.res_name),
                            "subject": "Today %s Activity" % rec.activity_type_id.name,
                            "email_to": rec.user_id.email,
                        }
                    ).send(auto_commit=False)

    @api.onchange("res_model", "res_name")
    def _compute_res_id(self):
        """Compute the res id for the document"""
        for rec in self:
            if not rec.res_id:
                if rec.res_model and rec.res_name:
                    res_model_name = self.env["ir.model"].search(
                        [("model", "=", rec.res_model)]
                    )
                    res_model_id = self.env[res_model_name.model].search(
                        [("name", "=", rec.res_name)]
                    )
                    for res in res_model_id:
                        rec.res_id = res.id
                else:
                    return
            else:
                return

    def activity_cancel(self):
        """cancel activity"""
        for rec in self:
            if rec.state == "cancel":
                raise UserError(_("You Cant Cancelled this activity %s") % rec.res_name)
            else:
                rec.action_cancel()

    def activity_done(self):
        """done activity"""
        for rec in self:
            if rec.state == "done":
                raise UserError(_("You Cant Cancelled this activity %s") % rec.res_name)
            else:
                rec._action_done()

    @api.model
    def action_set_activity_done(self, message):
        # self._action_done()
        for rec in self:
            rec.activity_done_feedback = message if message else False
            rec.activity_done()

    def get_activity_count(self):
        """get the activity count details"""
        activity = self.env["mail.activity"]
        all = activity.search([])
        planned = activity.search([("state", "=", "planned")])
        overdue = activity.search([("state", "=", "overdue")])
        today = activity.search([("state", "=", "today")])
        done = activity.search([("state", "=", "done"), ("active", "=", False)])
        cancel = activity.search([("state", "=", "cancel")])
        return {
            "len_all": len(all),
            "len_overdue": len(overdue),
            "len_planned": len(planned),
            "len_today": len(today),
            "len_done": len(done),
            "len_cancel": len(cancel),
        }

    def get_activity(self, id):
        """Function for to get the activity"""
        activity = self.env["mail.activity"].search([("id", "=", id)])
        return {"model": activity.res_model, "res_id": activity.res_id}

    def action_launch_feedback_wizard(self):
        return {
            'name': _('Activity Feedback'),
            'type': 'ir.actions.act_window',
            'res_model': 'activity.feedback',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_activity_id': self.id,
            },
        }

    def action_task_status(self):
        if not self.res_model_id.model == 'project.task':
            return
        task_id = self.document_id
        all_activity = self.sudo().search(
            [('document_id', '=', task_id.id), ('res_model_id.model', '=', 'project.task')])
        if all([activity.state == 'done' for activity in all_activity]):
            task_id.state = 'done'
        else:
            task_id.state = 'in_progress'

    def _action_done(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            # extract value to generate next activities
            if activity.force_next:
                Activity = self.env['mail.activity'].with_context(activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
                vals = Activity.default_get(Activity.fields_get())

                vals.update({
                    'previous_activity_type_id': activity.activity_type_id.id,
                    'res_id': activity.res_id,
                    'res_model': activity.res_model,
                    'res_model_id': self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity = Activity.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )

            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            messages |= activity_message

        next_activities = self.env['mail.activity'].create(next_activities_values)
        self.state = 'done'
        self.validate_timesheet()
        self.action_task_status()

        return messages, next_activities

    # def _action_done(self, feedback=False, attachment_ids=None):
    #     """action done function: rewrite the function"""
    #     self.state = 'done'
    #     self.validate_timesheet()
    #     self.action_task_status()
    #     res = super()._action_done()
    #     return res

    def validate_timesheet(self):
        if self.state == 'done':
            timesheet_ids = self.env['account.analytic.line'].sudo().search([
                ('activity_id', '=', self.id),
                ('project_id', '=', False)
            ])
            for t in timesheet_ids:
                t.write({
                    'project_id': t.project_id.id
                })

    def action_cancel(self):
        """cancel activities"""
        print('clicked')
        for rec in self:
            print(rec.res_model_id.model)
            task = self.env[f'{rec.res_model_id.model}'].search([('id', '=', rec.res_id)], limit=1)
            if task:
                print(task.name)
        # for rec in self:
        #     rec.state = "cancel"

    @api.depends("state")
    def _onchange_state(self):
        """change state and type"""
        for rec in self:
            rec.type = rec.state
