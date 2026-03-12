# -*- coding: utf-8 -*-
import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    job_quotation = fields.Boolean(string='Is Job Quotation',default=True)
    job_count=fields.Integer(compute="_get_job_orders")
    is_technical_submittal = fields.Boolean(string='Technical Submittal')
    ts_project = fields.Char(string='Project')
    ts_location = fields.Char(string='Location')
    ts_owner = fields.Char(string='Owner')
    ts_project_mgmt = fields.Char(string='Project Management')
    ts_consultant = fields.Char(string='Consultant')
    ts_mep_consultant = fields.Char(string='MEP Consultant')
    ts_main_consultant = fields.Char(string='Main Consultant')
    ts_mep_contractor = fields.Char(string='MEP Contractor')
    ts_designed_panels = fields.Char(string='Designed Panels')
    ts_reference_no = fields.Char(string='Reference No.')
    show_job_order_button=fields.Boolean(compute="calculated_show_job_order")

    direct_sale=fields.Boolean(string="Direct Sale")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        get_job_orders=self.env['quotation.job.order'].sudo().search([('quotation_no','=',self.ids[0])])

        if get_job_orders:
            invoice_vals['job_order_ids']=get_job_orders.ids
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_inv:
            invoice_vals['show_job_no'] = get_highest_inv.show_job_no

        return invoice_vals



    @api.onchange('direct_sale')
    def set_job_quotation(self):
        for rec in self:
            if rec.direct_sale==True:
                rec.job_quotation=False
            else:
                rec.job_quotation =True

    # breaker=fields.Char(string="Breaker")
    # elr=fields.Char(string="ELR")
    # enclosure=fields.Char(string="Enclosure")
    # brand=fields.Char(string="Brand")

    @api.depends('state')
    def calculated_show_job_order(self):
        # get_created_job_order=self.env['quotation.job.order'].sudo().search([('state','!=','cancelled'),('quotation_no','=',self.id)])
        self.show_job_order_button=False
        for line in self.order_line:
            if line.product_uom_qty-line.job_order_qty>0:
                self.show_job_order_button=True
                break;




    @api.depends('state')
    def _get_job_orders(self):
        for rec in self:
            get_job_orders=self.env['quotation.job.order'].sudo().search_count([('quotation_no','=',rec.id)])
            rec.job_count=get_job_orders

    def show_job_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("cpabooks_job_order.action_job_orders")

        if self.job_count > 1:
            action['domain'] = [('quotation_no', '=', self.id)]
        else:
            form_view = [(self.env.ref('cpabooks_job_order.view_job_order_form').id, 'form')]
            get_job_order=self.env['quotation.job.order'].sudo().search([('quotation_no','=',self.id)])
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = get_job_order.id
        action['context'] = dict(self._context, default_quotation_no=self.id, create=False)
        return action
        # form_view_id = self.env.ref("cpabooks_job_order.view_job_order_form").id
        # return {
        #     'name': _('Details'),
        #     'view_type': 'form',
        #     'view_mode': 'tree, form',
        #     'res_model': 'quotation.job.order',
        #     'views': [(form_view_id, 'form'), (False, 'tree')],
        #     'type': 'ir.actions.act_window',
        #     # 'res_id': self.id,
        #     'target': 'current',
        # }


    def confirm_sale_order(self):
        for rec in self:
            chk_create_project_field = self.env['ir.model.fields'].sudo().search([('name','=',"is_project_create"),
                                                                                  ('model_id', '=', self.env['ir.model'].sudo().search([('model', '=', 'sale.order')],limit=1).id)])
            if chk_create_project_field:
                if self.is_project_create and not self.project_id:
                    project_val = {
                        'name': self.name,
                        'label_tasks': "Task",
                        'user_id': self.env.user.id,
                        'partner_id': self.partner_id.id,
                        'privacy_visibility': 'portal',

                    }
                    project = self.env['project.project'].sudo().create(project_val)

                    analytic_acc_val = {
                        'name': project.name,
                        'partner_id': project.partner_id.id
                    }
                    analytic_acc = self.env['account.analytic.account'].sudo().create(analytic_acc_val)

                    project.analytic_account_id = analytic_acc.id

                    # self.project_name = project.name
                    self.project_id = project.id
                    self.analytic_account_id = project.analytic_account_id.id
            rec.state='sale'

    def action_cancel(self):
        delivery=sum(self.order_line.mapped('qty_delivered'))
        if delivery>0:
            raise ValidationError(_("To Cancel Sale Order You Need to Cancel All Delivery First"))
        else:
            return super(SaleOrder, self).action_cancel()






    def action_create_job_order(self):
        form_view_id = self.env.ref("cpabooks_job_order.view_job_order_form").id
        job_lines=[]
        for line in self.order_line:
            qty=line.product_uom_qty-line.job_order_qty
            if qty>0:
                job_line={
                    'line_no':line.line_no,
                    'product_id':line.product_id.id,
                    'name':line.name,
                    'product_uom':line.product_uom.id,
                    'product_uom_qty':line.product_uom_qty-line.job_order_qty,
                    # 'remaining_qty':line.remaining_qty,
                    'quotation_line_id':line.id
                }
                job_lines.append(job_line)
        job={
            'default_partner_id':self.partner_id.id,
            'default_project_id':self.project_id.id,
            'default_enquiry_number':self.enquiry_number,
            'default_attention':self.attention,
            'default_subject':self.subject,
            'default_delivery':self.delivery_detail,
            'default_make':self.make_detail,
            'default_bank_detail_enable':self.bank_detail_enable,
            'default_quotation_no':self.id,
            'default_validity_date':self.validity_date,
            'default_job_order_date':datetime.datetime.now().date(),
            'default_order_line':job_lines,
            'default_warehouse_id':self.warehouse_id.id,
            'default_sale_person':self.user_id.id
        }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'quotation.job.order',
            'views': [(form_view_id, 'form')],
            'target': 'current',
            'context':job
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    remaining_qty=fields.Float(string="Remaining Qty",copy=False)
    job_order_qty=fields.Float(string="Job Order Qty",copy=False)

