import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HelpdeskExtend(models.Model):
    _inherit = 'helpdesk.ticket'

    approver_id = fields.Many2one("res.users", string="Approver")
    ticket_state = fields.Selection([
        ('draft', 'Pending Review'),
        # ('new', 'New'),
        # ('approve', 'Approve'),
        # ('reviewed', 'Reviewed'),
        ('submit_for_approval', 'Pending Approval'),
        ('dev', 'Development In-Progress'),
        ('test', 'Pending Dev_test'),
        ('updating', 'Pending Client_update'),
        ('done', 'Updated to clients'),
        ('cancel', 'Cancelled')
    ],
        string="Ticket Status",
        tracking=True,
        default='draft', readonly=1)

    show_approve_btn = fields.Boolean(compute="btn_approve_viewer")

    # data_fill = fields.Many2one('res.users', domain=lambda self: self.updatedb())

    # def updatedb(self):
    #     get_all_ticket=self.env['helpdesk.ticket'].search([])
    #
    #     for line in get_all_ticket:
    #         line.ticket_state='draft'


    def get_reviewed(self):
        for rec in self:
            rec.ticket_state = "reviewed"
            stage = self.env['helpdesk.stage'].search([('ticket_state','=',rec.ticket_state)],limit=1)
            rec.stage_id = stage.id

    @api.model
    def create(self, vals):
        stage = self.env['helpdesk.stage'].search([('ticket_state', '=', self.ticket_state)], limit=1)
        vals['stage_id'] = stage.id if stage else False
        return super(HelpdeskExtend, self).create(vals)


    @api.model
    def write(self, vals):
        specific_fields = ['dev', 'partner_id']
        if vals and any(field in specific_fields for field in vals.keys()):
            vals['ticket_state'] = "draft"

        return super(HelpdeskExtend, self).write(vals)

    @api.depends('ticket_state')
    def btn_approve_viewer(self):
        for rec in self:
            rec.show_approve_btn = False
            if self.env.user.id == rec.approver_id.id:
                rec.show_approve_btn = True

    # def set_approver(self):
    #     for rec in self:
    #         for line in rec.require_items:
    #             rec.approver_id=line.task_id.approver_user_id.id
    #             break;

    @api.onchange('project')
    def set_approver(self):
        for rec in self:
            rec.approver_id = rec.project.approver_user_id.id

    def submit_for_approval(self):
        # return True
        for rec in self:
            if not rec.approver_id:
                raise ValidationError(_("Please set approver first..."))
            elif not rec.timesheet_ids:
                raise ValidationError(_("Please set work time duration first..."))
            else:
                rec.ticket_state = "submit_for_approval"
            stage = self.env['helpdesk.stage'].search([('ticket_state','=',rec.ticket_state)],limit=1)
            rec.stage_id = stage.id

    # def btn_cancel(self):
    #     for rec in self:
    #         rec.ticket_state="cancel"

    def btn_initial(self):
        for rec in self:
            rec.ticket_state = "draft"
            stage = self.env['helpdesk.stage'].search([('ticket_state','=',rec.ticket_state)],limit=1)
            rec.stage_id = stage.id

    def btn_approve(self):
        for rec in self:
            rec.ticket_state = "dev"
            stage = self.env['helpdesk.stage'].search([('ticket_state','=',rec.ticket_state)],limit=1)
            rec.stage_id = stage.id

    # @api.onchange("stage_id")
    # def chk_ticket_state(self):
    #     for rec in self:
    #         if rec.ticket_state not in ('draft', 'approve', 'cancel'):
    #             raise ValidationError(
    #                 "Ticket status need to be in Draft or Approved or Cancelled state to change working state")


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    tech_module_id = fields.Many2one('ir.module.module', 'Module')
