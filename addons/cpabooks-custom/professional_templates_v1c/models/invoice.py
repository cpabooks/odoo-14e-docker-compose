""" -*- coding: utf-8 -*-
License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
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
# © 2017 Bernard K Too<bernard.too@optima.co.ke>"""
import datetime

from num2words import num2words

from odoo import _, api, fields, models


class InvoiceTemplates(models.Model):
    _inherit = ["account.move"]

    subject=fields.Char(string="Subject")
    project_id=fields.Many2one('project.project',string="Project Name")
    # po_no=fields.Many2many('purchase.order',string="LPO No.")
    lpo_no=fields.Char(string="PO No.")
    show_po_no=fields.Boolean(default=True, string="Show PO No.")
    show_title = fields.Boolean(default=1, string="Show Title")
    show_trn=fields.Boolean(default=1, string="Show TRN")
    show_theme_color=fields.Boolean(default=1, string="Show Theme Color")
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')
    show_due_date = fields.Boolean(default=False, string="Show Due Date")
    show_sales_person = fields.Boolean(default=False, string="Show Sales Person")
    payment_mode = fields.Many2one('account.payment.method',string='Payment Mode')
    for_left=fields.Boolean(string="For Left")
    for_right = fields.Boolean(string="For Right")
    additional_note = fields.Text(string="Additional Note")
    show_additional_note=fields.Boolean(string="Show Additional Note")
    show_delivery_address=fields.Boolean(string="Show Delivery Address")
    delivery_mode=fields.Many2one('delivery.mode',string="Delivery Mode")
    delivery_date=fields.Datetime(string='Delivery Date')
    do_no = fields.Text('Do No.')

    show_subject=fields.Boolean(default=False,string="Show Subject")
    delivery_address=fields.Many2one('res.partner',string="Delivery Address")
    delivery_person=fields.Many2one('res.partner',string="Delivery Person")
    for_right = fields.Boolean(string="For Right")
    hide_global_discount = fields.Boolean(string="Hide Global Discount")
    show_project=fields.Boolean(default=True,string="Show Project")
    show_do_no=fields.Boolean(default=True,string="Show DO No.")

    #Field to store delivery name
    delivery_no = fields.Char(string='Delivery No.', readonly=False)
    #bank details
    bank_detail_enable = fields.Boolean('Show Bank Details on Invoice Report', default=lambda self: self.get_default_bank_detail_enable)
    #Signature
    approve_by = fields.Many2one('res.users', 'Approved By')
    prepared_by = fields.Many2one('res.users', 'Prepared By')
    stamp = fields.Binary('stamp', compute='_get_stamp')
    previous_balance = fields.Float('Previous Balance', compute="_compute_previous_balance")
    is_print_currency_id = fields.Boolean('Print Currency', default=True)
    is_print_previous_balance = fields.Boolean('Print Previous Balance', default=True)
    is_show_product_description = fields.Boolean('Show Product Description', default=True)
    is_show_header_footer = fields.Boolean('Show Header & Footer', default=True)
    is_show_accounting_date = fields.Boolean('Show Accounting Date')
    amount_paid = fields.Monetary('Total Paid', currency_field='currency_id')

    # note = fields.Text(default=lambda self: self.get_notes())

    # def get_notes(self):
    #     return "We hope our quotation are in line with your requirements & look forward to hear from you\n\n\n\n\nFor," + self.env.company.name

    def action_compute_paid_amt(self):
        invoices = self.env['account.move'].search([
            ('state', '=', 'posted')
        ])
        for inv in invoices:
            inv.amount_paid = inv.amount_total - inv.amount_residual
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Computed amounts for {len(invoices)} Invoices',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_post(self):
        res = super(InvoiceTemplates, self).action_post()
        if self.invoice_has_outstanding:
            pay_term_lines = self.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('ref', '=', self.name),
                ('partner_id', '=', self.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]
            line = self.env['account.move.line'].search(domain)
            if line:
                for l in line:
                    self.js_assign_outstanding_line(l.id)
        return res

    def _compute_previous_balance(self):
        for rec in self:
            rec.previous_balance = 0.0
            if rec.partner_id:
                account_ids = self.env['account.account'].search([
                    ('user_type_id.name', 'in', ('Receivable', 'Payable'))
                ])
                lines = self.env['account.move.line'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('account_id', 'in', account_ids.ids),
                    ('move_id', 'not in', [rec.id]),
                    ('move_id.state', 'not in', ['draft', 'cancel']),
                ])
                if lines:
                    rec.previous_balance = sum(lines.mapped('balance'))

    def _move_autocomplete_invoice_lines_values(self):
        ''' This method recomputes dynamic lines on the current journal entry that include taxes, cash rounding
        and payment terms lines.
        '''
        self.ensure_one()

        for line in self.line_ids:
            # Do something only on invoice lines.
            if line.exclude_from_invoice_tab:
                continue

            # Shortcut to load the demo data.
            # Doing line.account_id triggers a default_get(['account_id']) that could returns a result.
            # A section / note must not have an account_id set.
            if not line._cache.get('account_id') and not line.display_type and not line._origin:
                line.account_id = line._get_computed_account() or self.journal_id.default_account_id
            if line.product_id and not line._cache.get('name') and (line.name == '' or line.name=='/'):
                line.name = line._get_computed_name()

            # Compute the account before the partner_id
            # In case account_followup is installed
            # Setting the partner will get the account_id in cache
            # If the account_id is not in cache, it will trigger the default value
            # Which is wrong in some case
            # It's better to set the account_id before the partner_id
            # Ensure related fields are well copied.
            line.partner_id = self.partner_id
            line.date = self.date
            line.recompute_tax_line = True
            line.currency_id = self.currency_id

        self.line_ids._onchange_price_subtotal()
        self._recompute_dynamic_lines(recompute_all_taxes=True)

        values = self._convert_to_write(self._cache)
        values.pop('invoice_line_ids', None)
        return values

    def _get_stamp(self):
        for rec in self:
            rec.stamp = rec.approve_by.user_stamp or rec.prepared_by.user_stamp or False

    @api.onchange('company_id')
    def get_default_approve_and_prepared_by(self):
        for rec in self:
            last_val = self.env['sale.order'].search([], limit=1)
            if last_val:
                rec.approve_by = last_val.approve_by
                rec.prepared_by = last_val.prepared_by
            else:
                rec.approve_by = False
                rec.prepared_by = False

    def _check_isntallation(self):
        for rec in self:
            is_module_install=self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_digital_signature_pt')])
            return True if is_module_install else False

    #Baank details
    def get_default_bank_detail_enable(self):
        for rec in self:
            last_inv = self.env['account.move'].search([],limit=1)
            rec.bank_detail_enable = last_inv.bank_detail_enable or False


            # record.delivery_no = sale_order.mapped('delivery') if latest_sale_order else False

    @api.model
    def default_get(self, fields):
        result = super(InvoiceTemplates, self).default_get(fields)
        get_highest_inv = self.env['account.move'].sudo().search(
            [('move_type', '=', 'out_invoice')], limit=1,
            order='id desc')
        if get_highest_inv:
            result.update({
                'show_delivery_address': get_highest_inv.show_delivery_address,
                'is_print_currency_id': get_highest_inv.is_print_currency_id,
                'is_print_previous_balance': get_highest_inv.is_print_previous_balance,
                'show_sales_person': get_highest_inv.show_sales_person,
                'is_show_product_description': get_highest_inv.is_show_product_description,
                'is_show_header_footer': get_highest_inv.is_show_header_footer,
                'show_do_no': get_highest_inv.show_do_no,
                'is_show_accounting_date': get_highest_inv.is_show_accounting_date,
            })
        immediate_payment_id = self.env['account.payment.term'].search([
            ('name', '=', 'Immediate Payment')
        ],limit=1)
        if immediate_payment_id:
            result.update({
                'invoice_payment_term_id': immediate_payment_id.id
            })
        return result


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
            'professional_templates_v1c.df_style_for_all_reports')

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
                'professional_templates_v1c.df_style_for_all_reports')
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

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','account.move'),('company_id','=',self.env.company.id)])
        return get_signature_data

    @api.model
    def get_do(self):
        if self.invoice_origin:
            get_do_all = self.env['stock.picking'].sudo().search(
                [('origin', '=', self.invoice_origin), ('state', '=', 'done')])
            get_do = ""
            for rec in get_do_all:
                get_do += rec.name + ', '
            return get_do
        else:
            get_do = []

    def check_bank_detail_existency(self):
        if 'bank_detail_enable' in self.env['product.product']._fields:
            return True
        else:
            return False
            
class InvoiceLineTemplate(models.Model):
    _inherit = ["account.move.line"]

    @api.depends('move_id.is_show_product_description')
    @api.onchange('product_id')
    def get_prod_des(self):
        for rec in self:
            if rec.move_id.is_show_product_description and rec.product_id and rec.product_id.prod_description:
                rec.name = f'{rec.product_id.name} \n {rec.product_id.prod_description}'
            else:
                rec.name = f'{rec.product_id.name}'


    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.move_id.invoice_line_ids:
                if line_rec.display_type not in ('line_section', 'line_note'):
                    line_rec.line_no = line_num
                    line_num += 1

    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)
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
