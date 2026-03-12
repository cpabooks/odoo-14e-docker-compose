from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DailySiteReport(models.Model):
    _name = "daily.site.report"
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
    daily_site_report_line = fields.One2many('daily.site.report.line', 'report_id', string='Site Report Lines')

    description=fields.Text(string="Description")
    recommendation=fields.Text(string="Recommendations / Suggestions")
    # attachment_ids = fields.Binary("Photos", required=True)
    image = fields.Many2many('ir.attachment', string="Photo")
    images=fields.One2many('daily.image','report_id',string="Photos")

    def get_issued_material(self):
        get_issue=self.env['stock.picking'].sudo().search([('issue_project_id','=',self.project_no.id),('state','=','done')])
        issued_list=[]
        for data in get_issue:
            for rec in data.move_ids_without_package:
                vals={
                    'date_done':data.date_done.date(),
                    'note_no':data.name,
                    'product_name':rec.product_id.name,
                    'quantity':rec.quantity_done,
                    'uom':rec.product_uom.name,
                    'rate':rec.rate,
                    'amount':rec.amount

                }
                issued_list.append(vals)
        return issued_list


    def get_material_used_and_issued(self):
        get_used=self.daily_site_report_line
        get_issue = self.env['stock.picking'].sudo().search(
            [('issue_project_id', '=', self.project_no.id), ('state', '=', 'done')])
        existing_get_issued=self.env['stock.move']
        existing_get_issued = get_issue.move_ids_without_package
        val_list=[]
        for used in get_used:
            vals = {
                'item': used.product_id.name,
                'planned_qty': used.product_qty,
                'issued_qty': 0,
                'balance': used.product_qty,
                'remarks': used.remarks
            }
            val_list.append(vals)
        if val_list:
            for issued in get_issue.move_ids_without_package:
                for val in val_list:
                    if val['item'] == issued.product_id.name:
                        val['issued_qty']=val['issued_qty']+issued.quantity_done
                        val['balance']=val['balance']-issued.quantity_done
                        existing_get_issued=get_issue.move_ids_without_package-issued


        if existing_get_issued:
            for existing in existing_get_issued:
                vals = {
                    'item': existing.product_id.name,
                    'planned_qty': 0.0,
                    'issued_qty': existing.quantity_done,
                    'balance': (-1) * issued.quantity_done,
                    'remarks': ''
                }
                val_list.append(vals)
        return val_list



    # def get_material_used_and_issued(self):
    #     get_used=self.daily_site_report_line
    #     get_issue = self.env['stock.picking'].sudo().search(
    #         [('issue_project_id', '=', self.project_no.id), ('state', '=', 'done')])
    #     existing_get_issued=self.env['stock.move']
    #     val_list=[]
    #     for used in get_used:
    #
    #         for issued in get_issue.move_ids_without_package:
    #             if used.product_id==issued.product_id:
    #                 vals = {
    #                     'item': used.product_id.name,
    #                     'planned_qty': used.product_qty,
    #                     'issued_qty': issued.quantity_done,
    #                     'balance': used.product_qty-issued.quantity_done,
    #                     'remarks': used.remarks
    #                 }
    #                 existing_get_issued=get_issue.move_ids_without_package-issued
    #                 val_list.append(vals)
    #             else:
    #                 vals = {
    #                     'item': used.product_id.name,
    #                     'planned_qty': used.product_qty,
    #                     'issued_qty': 0,
    #                     'balance': (-1)*used.product_qty,
    #                     'remarks': used.remarks
    #                 }
    #                 existing_get_issued = get_issue.move_ids_without_package - issued
    #                 val_list.append(vals)
    #     if existing_get_issued:
    #         for existing in existing_get_issued:
    #             vals = {
    #                 'item': existing.product_id.name,
    #                 'planned_qty': 0.0,
    #                 'issued_qty': existing.quantity_done,
    #                 'balance': (-1)* issued.quantity_done,
    #                 'remarks': ''
    #             }
    #             val_list.append(vals)
    #     return val_list




    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('daily.site.report') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('daily.site.report')

        get_sequence_app_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_sequences')])
        if get_sequence_app_installed:
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('daily_site_report')
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for Daily Site Report"))
            vals['name'] = get_sequence or _('/')
        result = super(DailySiteReport, self).create(vals)
        return result


class DailySiteReportLine(models.Model):
    _name = "daily.site.report.line"

    report_id = fields.Many2one("daily.site.report", string='Report Reference', index=True, required=True,
                                     ondelete='cascade')
    product_id = fields.Many2one('product.product', string="ITEM#")
    product_qty=fields.Float(string="QTY")
    remarks = fields.Char(string="REMARKS")

class DailySiteReportImages(models.Model):
    _name="daily.image"

    report_id=fields.Many2one('daily.site.report')
    image = fields.Binary(string="Photo")

