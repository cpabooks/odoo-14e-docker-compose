# -*- coding: utf-8 -*-
"""
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).
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
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
"""
import datetime
import re

from num2words import num2words

from odoo import _, api, fields, models


class SO(models.Model):
    """Sales Order @Model inherited to add fields and methods for report
    printing."""
    _inherit = ["sale.order"]

    po_ids=fields.Many2many('purchase.order',string='LPO No.')
    lpo_no=fields.Char(string='PO No.')
    show_po_no=fields.Boolean(string="Show PO No.")
    enquiry_number = fields.Char(string='Enquiry Number')
    subject = fields.Char(string='Subject')
    greeting_note = fields.Char(string="Greeting Note", default="Dear Sir,")
    attention = fields.Char(string='Attention')
    delivery_detail = fields.Char(string='Delivery')
    make_detail = fields.Char(string='Make')
    asset_no = fields.Char(string="Asset No")
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')
    exclusion = fields.Char(string="Exclusions")

    cust_project_id = fields.Many2one('project.project', string="Project Name")

    is_technical_spec = fields.Boolean(string='Technical Spec')
    technical_spec = fields.One2many('technical.spec', 'order_id', string="Technical Spec")

    show_attention = fields.Boolean(default=1, string="Show Attention")
    attention_left = fields.Boolean(default=0, string="Attention Left")
    attention_right = fields.Boolean(default=1, string="Attention Right")
    show_order_date = fields.Boolean(default=1, string="Show Order Date")
    show_expiration = fields.Boolean(default=1, string="Show Expiration")
    show_asset_no = fields.Boolean(default=0, string="Show Asset No")
    show_greeting_note = fields.Boolean(default=0, string="Show Greeting Note")
    show_exclusion = fields.Boolean(default=0, string="Show Exclusion")
    show_validity = fields.Boolean(default=0, string="Show Validity")
    show_warranty = fields.Boolean(default=0, string="Show Warranty")
    warranty = fields.Char(string='Warranty')
    validity_days = fields.Integer(string="Validity", compute='_get_validity_days', store=True)
    project_id = fields.Many2one('project.project', string='Job Order', readonly=False)


    # Field for storing delivery name
    delivery = fields.Char('Delivery Name')
    job = fields.Char('Job Name')

    is_item_code = fields.Boolean('Show Item Code(Form)')
    show_part = fields.Boolean('show Part')

    # @api.onchange('show_part')
    # def set_show_part(self):
    #     order_line = self.env['sale.order.line'].search('order_id','=',self.id)
    #     print(order_line)

    # @api.onchange('show_part')
    # def set_show_part(self):
    #     for rec in self:
    #         if rec.show_part:
    #             rec.order_line.show_part = True
    #         elif not rec.show_part:
    #             rec.order_line.show_part = False

    @api.onchange('company_id')
    def get_default_is_show_part(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if get_highest_qt:
            self.show_part = get_highest_qt.show_part

    @api.onchange('company_id')
    def get_default_is_item_code(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if get_highest_qt:
            self.is_item_code = get_highest_qt.is_item_code

    @api.onchange('company_id')
    def get_default_show_exclusion(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_exclusion = get_highest_qt.show_exclusion

    @api.depends('validity_date', 'date_order')
    def _get_validity_days(self):
        for rec in self:
            if rec.validity_date and rec.date_order:
                days_difference = (rec.validity_date - rec.date_order.date()).days
            else:
                days_difference = 0
            rec.validity_days = days_difference

    @api.onchange('company_id')
    def get_default_show_greeting_note(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_greeting_note = get_highest_qt.show_greeting_note

    @api.onchange('company_id')
    def get_default_show_asset_no(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_asset_no = get_highest_qt.show_asset_no

    @api.onchange('company_id')
    def get_default_show_expiration(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_expiration = get_highest_qt.show_expiration

    @api.onchange('company_id')
    def get_default_show_attention(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_attention = get_highest_qt.show_attention

    @api.onchange('company_id')
    def get_default_show_order_date(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_order_date = get_highest_qt.show_order_date

    @api.onchange('company_id')
    def get_default_show_po(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_po_no = get_highest_qt.show_po_no

    @api.onchange('partner_id')
    def _set_default_technical_spec(self):
        get_highest_so = self.env['sale.order'].sudo().search(
            [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.company_id.id)], limit=1,
            order='id desc')

        if get_highest_so:
            self.is_technical_spec = get_highest_so.is_technical_spec
            self.technical_spec = get_highest_so.technical_spec
        else:
            self.is_technical_spec = False
            self.technical_spec = None

    def get_t_and_c(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
        if get_model:
            get_field = self.env['ir.model.fields'].sudo().search(
                [('name', '=', "t_and_c"), ('model_id', '=', get_model.id)])

            if get_field and self.show_t_and_c:
                return self.t_and_c
            else:
                return []

    def get_warm_regards(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
        if get_model:
            get_field = self.env['ir.model.fields'].sudo().search(
                [('name', '=', "warm_regards"), ('model_id', '=', get_model.id)])

            if get_field and self.show_warm_regards:
                return self.warm_regards
            else:
                return []

    def is_html_empty(self, html_content):
        """Check if a html content is empty. If there are only formatting tags or
        a void content return True. Famous use case if a '<p><br></p>' added by
        some web editor.

        :param str html_content: html content, coming from example from an HTML field
        :returns: bool, True if no content found or if containing only void formatting tags
        """
        if not html_content:
            return True
        tag_re = re.compile(r'\<\s*\/?(?:p|div|span|br|b|i)\s*/?\s*\>')
        return not bool(re.sub(tag_re, '', html_content).strip())

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount_total)).replace('And', 'and')

    def _prepare_invoice(self):
        invoice_vals = super(SO, self)._prepare_invoice()
        if self.cust_project_id:
            invoice_vals['project_id'] = self.cust_project_id
        if self.lpo_no:
            invoice_vals['lpo_no'] = self.lpo_no
        if self.show_po_no:
            invoice_vals['show_po_no'] =True
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        get_delivery = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.name), ('state', '=', 'done')], order="id desc", limit=1)
        if get_highest_inv:
            invoice_vals['show_delivery_address'] = get_highest_inv.show_delivery_address
            invoice_vals['show_subject'] = get_highest_inv.show_subject
            invoice_vals['show_project'] = get_highest_inv.show_project
            # invoice_vals['show_po_no'] = get_highest_inv.show_po_no
            # invoice_vals['show_job_no'] = get_highest_inv.show_job_no
            invoice_vals['show_additional_note'] = get_highest_inv.show_additional_note
            invoice_vals['for_left'] = get_highest_inv.for_left
            invoice_vals['for_right'] = get_highest_inv.for_right
            # invoice_vals['show_po_no'] = get_highest_inv.show_po_no
        if get_delivery:
            invoice_vals['delivery_date'] = get_delivery.scheduled_date
        else:
            invoice_vals['delivery_date'] = datetime.datetime.now()

        return invoice_vals

    @api.onchange('partner_id')
    def onchange_partner_style(self):
        """ @onchage method to assign style to a document based on chosen partner"""

        self.style = self.partner_id.style or self.env.user.company_id.df_style or \
                     self.env.ref('professional_templates.df_style_for_all_reports').id

    style = fields.Many2one(
        'report.template.settings',
        'Quote/Order Style',
        help="Select Style to use when printing the Sales Order or Quote",
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
        "The total amount in words is automatically generated by the system",
        compute='_compute_num2words')

    def _compute_num2words(self):
        for rec in self:
            style = rec.style or rec.partner_id.style or \
                    rec.env.user.company_id.df_style or rec.env.ref(
                'professional_templates.df_style_for_all_reports')
            if style and style.aiw_report:
                try:
                    rec.amount_words = (
                            num2words(rec.amount_total, lang=rec.partner_id.lang or
                                                             'en') +
                            ' ' + (rec.currency_id.currency_name or '')).upper()
                except NotImplementedError:
                    rec.amount_words = (
                            num2words(rec.amount_total, lang='en') + ' ' +
                            (rec.currency_id.currency_name or '')).upper()
            else:
                rec.amount_words = _('Disabled')

    def _create_invoices(self, grouped=False, final=False):
        invoice_vals_prepare = super(SO, self)._create_invoices(grouped=grouped, final=final)
        invoice_vals_prepare['delivery_no'] = self.delivery
        # invoice_vals_prepare['job_no'] = self.job
        return invoice_vals_prepare


class SO_Line(models.Model):
    _inherit = "sale.order.line"

    is_item_code = fields.Boolean('Show Item Code', related='order_id.is_item_code')
    # item_id = fields.Many2many('sale.order')
    item_code = fields.Char('Item Code', compute='_get_item_code')
    show_part = fields.Boolean('Show Part')
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)

    def _get_item_code(self):
        for rec in self:
            if rec.product_id:
                rec.item_code = rec.product_id.item_code

    def check_tax_type(self):
        for rec in self:
            is_included = False
            for tax in rec.tax_id:
                if tax.price_include:
                    is_included = True
            return is_included

    def calculate_tax_amt(self):
        for rec in self:
            tax_amt = 0
            discount_amt = 0
            total_amt = rec.product_uom_qty * rec.price_unit
            if 'discount_method' in rec._fields.keys():

                if rec.discount_method == 'fix':
                    for tax in rec.tax_id:
                        if not tax.price_include:
                            tax_amt += ((total_amt - rec.discount_amount) * (tax.amount / 100))
                            total_amt -= tax_amt
                        else:
                            tax_amt += ((total_amt - rec.discount_amount) * (tax.amount / 105))
                            total_amt -= tax_amt
                else:
                    for tax in rec.tax_id:
                        if not tax.price_include:
                            tax_amt += ((total_amt - (total_amt * (rec.discount_amount / 100))) * (tax.amount / 100))
                            total_amt -= tax_amt
                        else:
                            tax_amt += ((total_amt - (total_amt * (rec.discount_amount / 105))) * (tax.amount / 105))
                            total_amt -= tax_amt
            else:
                for tax in rec.tax_id:
                    if not tax.price_include:
                        tax_amt += total_amt * (tax.amount / 100)
                        total_amt -= tax_amt
                    else:
                        tax_amt += total_amt * (tax.amount / 105)
                        total_amt -= tax_amt
            return tax_amt

    def get_after_discount_amt(self):
        for rec in self:
            after_disc_amt = rec.product_uom_qty * rec.price_unit
            total_amt = rec.product_uom_qty * rec.price_unit
            if 'discount_method' in rec._fields.keys() and rec.order_id.discount_type == 'line':
                if rec.discount_method == 'fix':
                    after_disc_amt = total_amt - rec.discount_amount
                else:
                    after_disc_amt = total_amt - (total_amt * (rec.discount_amount / 100))
            return after_disc_amt
