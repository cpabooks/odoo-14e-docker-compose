# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT section below).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
import datetime

from num2words import num2words

from odoo import _, api, fields, models


class InvoiceTemplates(models.Model):
    _inherit = ["account.move"]


    subject=fields.Char(string="Subject")
    project_id=fields.Many2one('project.project',string="Project Name")
    # po_no=fields.Many2many('purchase.order',string="LPO No.")
    lpo_no=fields.Char(string="PO No.")
    show_po_no=fields.Boolean(string="Show PO No.")
    show_title = fields.Boolean(default=1, string="Show Title")
    show_trn=fields.Boolean(default=1, string="Show TRN")
    show_theme_color=fields.Boolean(default=1, string="Show Theme Color")
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')
    show_due_date = fields.Boolean(default=1, string="Show Due Date")
    show_sales_person = fields.Boolean(default=1, string="Show Sales Person")
    payment_mode = fields.Many2one('account.payment.method',string='Payment Mode')
    for_left=fields.Boolean(string="For Left")
    for_right = fields.Boolean(string="For Right")
    additional_note = fields.Text(string="Additional Note")
    show_additional_note=fields.Boolean(string="Show Additional Note")
    show_delivery_address=fields.Boolean(string="Show Delivery Address")
    delivery_mode=fields.Many2one('delivery.mode',string="Delivery Mode")
    delivery_date=fields.Datetime(string='Delivery Date')

    show_subject=fields.Boolean(default=1,string="Show Subject")
    delivery_address=fields.Many2one('res.partner',string="Delivery Address")
    delivery_person=fields.Many2one('res.partner',string="Delivery Person")
    for_right = fields.Boolean(string="For Right")
    hide_global_discount = fields.Boolean(string="Hide Global Discount")
    show_project=fields.Boolean(default=1,string="Show Project")

    #Field to store delivery name
    delivery_no = fields.Char(string='Delivery No.', readonly=False)



            # record.delivery_no = sale_order.mapped('delivery') if latest_sale_order else False

    # @api.model
    # def default_get(self, fields):
    #     result = super(InvoiceTemplates, self).default_get(fields)
    #     get_highest_inv = self.env['account.move'].sudo().search(
    #         [('company_id', '=', self.env.company_id.id), ('move_type', '=', 'out_invoice')], limit=1,
    #         order='id desc')
    #     if get_highest_inv:
    #         result['show_delivery_address'] = get_highest_inv.show_delivery_address
    #     return result


    @api.onchange('company_id')
    def _get_delivery_date(self):
        if self.invoice_origin:
            get_delivery=self.env['stock.picking'].sudo().search([('origin','=',self.invoice_origin),('state','=','done')],order="id desc",limit=1)
            if get_delivery:
                self.delivery_date= get_delivery.scheduled_date
            else:
                self.delivery_date= datetime.datetime.now()
        else:
            self.delivery_date= datetime.datetime.now()

    def _get_receiver_details(self):
        for rec in self:
            get_receiver_details=self.env['stock.picking'].sudo().search([('origin','=',rec.invoice_origin)],order="id desc", limit=1)
            return get_receiver_details

    @api.onchange('company_id')
    def get_default_show_subject(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'),('state','!=','cancel')], limit=1,
            order='id desc')
        if get_highest_inv:
            self.show_subject = get_highest_inv.show_subject


    @api.onchange('company_id')
    def get_default_show_project(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_inv:
            self.show_project = get_highest_inv.show_project

    @api.onchange('company_id')
    def get_default_show_delivery_address(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'),('state','!=','cancel')], limit=1,
            order='id desc')
        if get_highest_inv:
            self.show_delivery_address = get_highest_inv.show_delivery_address

    @api.onchange('company_id')
    def get_default_add_note(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'),('state','!=','cancel')], limit=1,
            order='id desc')

        if get_highest_inv:
            self.show_additional_note = get_highest_inv.show_additional_note

    @api.onchange('company_id')
    def get_default_for(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')

        if get_highest_inv:
            self.for_left=get_highest_inv.for_left
            self.for_right=get_highest_inv.for_right

    @api.onchange('company_id')
    def get_default_po_no(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')

        if get_highest_inv:
            self.show_po_no = get_highest_inv.show_po_no

    # @api.onchange('company_id')
    # def get_default_job_no(self):
    #     get_highest_inv = self.env['account.move'].sudo().search(
    #         [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
    #         limit=1,
    #         order='id desc')
    #
    #     if get_highest_inv:
    #         self.show_job_no = get_highest_inv.show_job_no



    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount_total)).replace('And', 'and')
    @api.onchange('partner_id')
    def onchange_partner_style(self):
        self.style = self.partner_id.style or self.env.user.company_id.df_style or self.env.ref(
            'professional_templates.df_style_for_all_reports')

    @api.model
    def create(self, vals):
        res = super(InvoiceTemplates, self).create(vals)
        if res:  # trigger onchage after creating invoice to update the partner style
            res.onchange_partner_style()
        return res

    style = fields.Many2one(
        'report.template.settings',
        'Invoice Style',
        help="Select style to use when printing this invoice",
        default=lambda self: self.partner_id.style or self.env.user.company_id.
        df_style)
    project_title = fields.Char(
        'Title',
        help=
        "The title of your customer project or work you are doing for your customer"
    )
    amount_words = fields.Char(
        'Amount in Words:',
        help=
        "The invoice total amount in words is automatically generated by the system..few languages are supported currently",
        compute='_compute_num2words')

    def _compute_num2words(self):
        for rec in self:
            style = rec.style or rec.partner_id.style or rec.env.user.company_id.df_style or rec.env.ref(
                'professional_templates.df_style_for_all_reports')
            if style and style.aiw_report:
                try:
                    rec.amount_words = num2words(
                        rec.amount_total, lang=rec.partner_id.lang or 'en').upper()
                except NotImplementedError:
                    rec.amount_words = num2words(rec.amount_total,
                                                 lang='en').upper()
            else:
                rec.amount_words = _('DISABLED')

    @api.model
    def create(self, vals):
        for rec in self:
            qt = self.env['sale.order'].search([('id', '=', rec.id)])
            if qt:
                rec.delivery_no = qt.delivery

        return super(InvoiceTemplates, self).create(vals)
            
class InvoiceLineTemplate(models.Model):
    _inherit = ["account.move.line"]

    name = fields.Text(string='Label', tracking=True)

    def check_tax_type(self):
        for rec in self:
            is_included=False
            for tax in rec.tax_ids:
                if tax.price_include:
                    is_included=True
            return is_included

    def calculate_tax_amt(self):
        for rec in self:
            tax_amt = 0
            discount_amt = 0
            total_amt = rec.quantity * rec.price_unit
            if 'discount_method' in rec._fields.keys():

                if rec.discount_method == 'fix':
                    for tax in rec.tax_ids:
                        if not tax.price_include:
                            tax_amt += ((total_amt - rec.discount_amount) * (tax.amount / 100))
                            total_amt -= tax_amt
                        else:
                            tax_amt += ((total_amt - rec.discount_amount) * (tax.amount / 105))
                            total_amt -= tax_amt
                else:
                    for tax in rec.tax_ids:
                        if not tax.price_include:
                            tax_amt += ((total_amt - (total_amt * (rec.discount_amount / 100))) * (tax.amount / 100))
                            total_amt -= tax_amt
                        else:
                            tax_amt += ((total_amt - (total_amt * (rec.discount_amount / 105))) * (tax.amount / 105))
                            total_amt -= tax_amt
            else:
                for tax in rec.tax_ids:
                    if not tax.price_include:
                        tax_amt += total_amt * (tax.amount / 100)
                        total_amt -= tax_amt
                    else:
                        tax_amt += total_amt * (tax.amount / 105)
                        total_amt -= tax_amt
            return tax_amt

    def get_after_discount_amt(self):
        for rec in self:
            after_disc_amt=rec.quantity * rec.price_unit
            total_amt = rec.quantity * rec.price_unit
            if 'discount_method' in rec._fields.keys() and rec.move_id.discount_type=='line':
                if rec.discount_method=='fix':
                    after_disc_amt=total_amt-rec.discount_amount
                else:
                    after_disc_amt=total_amt-(total_amt*(rec.discount_amount/100))
            return after_disc_amt


# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"
#
#
#     # get delivery_no here
#     # def _prepare_invoice_values(self, order, name, amount, so_line):
#     #     invoice_vals = super()._prepare_invoice_values(order, name, amount, so_line)
#     #     delivery = self.env['stock.picking'].search(['name', '=', order.delivery])
#     #     job = self.env['quotation.job.order'].search([('name','=',order.job),('state','=','confirmed')])
#     #     invoice_vals.update({
#     #         'delivery_no': delivery.name if delivery.state == 'done' else '[Not Done yet!]',
#     #         'job_no': job.name if job else '[Not Done yet!]',
#     #     })
#     #     return invoice_vals
#
#     def _prepare_invoice_values(self, order, name, amount, so_line):
#         invoice_vals = super()._prepare_invoice_values(order, name, amount, so_line)
#         delivery = self.env['stock.picking'].search([('name', '=', order.delivery)])
#         job = self.env['quotation.job.order'].search([('name', '=', order.job), ('state', '=', 'confirmed')])
#         invoice_vals.update({
#             'delivery_no': delivery.name if delivery and delivery.state == 'done' else '[Not Done yet!]',
#             'job_no': job.name if job else '[Not Confirmed yet!]',
#         })
#         return invoice_vals
