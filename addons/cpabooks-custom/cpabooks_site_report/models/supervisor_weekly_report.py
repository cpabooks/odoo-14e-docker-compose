from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SupervisorWeeklyReport(models.Model):
    _name = "supervisor.weekly.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New'), copy=False, readonly=True)
    project_no = fields.Many2one("project.project", string="Project")
    location=fields.Char(string="Location")
    contact_no=fields.Char(string="Contact Number")
    plan_no=fields.Char(string="Plan Number")
    issue_date=fields.Datetime(string="Issue Date")
    due_date=fields.Datetime(string="Due Date")
    rev_date=fields.Datetime(string="Rev Date")
    rev_no=fields.Float(string="Rev No.")
    supervisor_weekly_report_line = fields.One2many('supervisor.weekly.report.line', 'report_id', string='Supervisor weekly Report Lines')

    description=fields.Text(string="Description")
    recommendation=fields.Text(string="Recommendations / Suggestions")
    # attachment_ids = fields.Binary("Photos", required=True)
    image = fields.Many2many('ir.attachment', string="Photo")
    images = fields.One2many('supervisor.weekly.image', 'report_id', string="Photos")


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('supervisor.weekly.report') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('supervisor.weekly.report')

        get_sequence_app_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_sequences')])
        if get_sequence_app_installed:
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('supervisor_weekly_report')
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for Supervisor Weekly Report"))
            vals['name'] = get_sequence or _('/')
        result = super(SupervisorWeeklyReport, self).create(vals)
        return result


class SupervisorWeeklyReportLine(models.Model):
    _name = "supervisor.weekly.report.line"

    report_id = fields.Many2one("supervisor.weekly.report", string='Report Reference', index=True, required=True,
                                     ondelete='cascade')
    product_id = fields.Many2one('product.product', string="ITEM#")
    # product_qty=fields.Float(string="QTY")
    req_qty = fields.Float(string="Req Qty")
    issued_qty = fields.Float(string="Issued Qty")
    balance_qty = fields.Float(string="Balance Qty")
    remarks = fields.Char(string="REMARKS")

class SupervisorWeeklySiteReportImages(models.Model):
    _name="supervisor.weekly.image"

    report_id=fields.Many2one('supervisor.weekly.report')
    image = fields.Binary(string="Photo")

