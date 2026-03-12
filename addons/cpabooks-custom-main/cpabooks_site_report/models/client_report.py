from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ClientReport(models.Model):
    _name = "client.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New'), copy=False, readonly=True)
    project_no = fields.Many2one("project.project", string="Project")
    client_name = fields.Many2one("res.partner",related="project_no.partner_id", string="Client Name")
    location=fields.Char(string="Location")
    contact_no=fields.Char(string="Contact Number")
    plan_no=fields.Char(string="Plan Number")
    issue_date=fields.Datetime(string="Issue Date")
    due_date=fields.Datetime(string="Due Date")
    rev_date=fields.Datetime(string="Rev Date")
    rev_no=fields.Float(string="Rev No.")
    client_report_line = fields.One2many('client.report.line', 'report_id', string='Site Report Lines')

    description=fields.Text(string="Description")
    recommendation=fields.Text(string="Recommendations / Suggestions")
    # attachment_ids = fields.Binary("Photos", required=True)
    image = fields.Many2many('ir.attachment', string="Photo")
    images = fields.One2many('client.image', 'report_id', string="Photos")


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('client.report') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('client.report')

        get_sequence_app_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_sequences')])
        if get_sequence_app_installed:
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('client_report')
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for Client Report"))
            vals['name'] = get_sequence or _('/')
        result = super(ClientReport, self).create(vals)
        return result


class ClientReportLine(models.Model):
    _name = "client.report.line"

    report_id = fields.Many2one("client.report", string='Report Reference', index=True, required=True,
                                     ondelete='cascade')
    product_id = fields.Many2one('product.product', string="ITEM#")
    product_qty=fields.Float(string="QTY")
    remarks = fields.Char(string="REMARKS")
class ClientReportImages(models.Model):
    _name="client.image"

    report_id=fields.Many2one('client.report')
    image = fields.Binary(string="Photo")
