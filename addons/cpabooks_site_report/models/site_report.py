from odoo import models, fields, api, _


class SiteReport(models.Model):
    _name = "site.report"
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
    site_report_line = fields.One2many('site.report.line', 'report_id', string='Site Report Lines')



    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('site.report') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('site.report')
        result = super(SiteReport, self).create(vals)
        return result


class SiteReportLine(models.Model):
    _name = "site.report.line"

    report_id = fields.Many2one("site.report", string='Report Reference', index=True, required=True,
                                     ondelete='cascade')
    product_id = fields.Many2one('product.product', string="ITEM#")
    product_qty=fields.Float(string="QTY")
    remarks = fields.Char(string="REMARKS")

