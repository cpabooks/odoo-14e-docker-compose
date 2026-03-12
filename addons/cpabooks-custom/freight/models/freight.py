
import logging
from itertools import groupby
import pytz
import time
import babel

import base64
import urllib
from odoo.osv.expression import get_unaccent_wrapper
import re

from odoo import api, fields, models, tools, SUPERUSER_ID, _
# from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipper = fields.Boolean('Customer')
    consignee = fields.Boolean('Vendor')
    agent = fields.Boolean('Agent')

class CustomerInvoice(models.Model):
    _inherit = 'account.move'

    freight_operation_id = fields.Many2one('freight.operation', string='Freight ID')

    # @api.onchange('freight_operation_id')
    # def _prepare_invoice_line(self, **optional_values):
    #     self.ensure_one()
    #     for rec in self.freight_operation_id.freight_line_ids:
    #         self.ensure_one()
    #         res = {
    #             # 'display_type': self.display_type,
    #             # 'sequence': self.sequence,
    #             # 'name': self.name,
    #             'product_id': rec.product_id.id,
    #             'product_uom_id': rec.product_uom.id,
    #             'quantity': rec.product_uom_qty,
    #             # 'discount': rec.discount,
    #             'price_unit': rec.price_unit,
    #             'tax_ids': [(6, 0, rec.product_id.taxes_id)],
    #             # 'analytic_account_id': rec.operation_id.analytic_account_id.id,
    #             # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
    #             'sale_line_ids': [(4, rec.id)],
    #             'port_of_loading': rec.port_of_loading,
    #             'port_of_delivery': rec.port_of_delivery,
    #
    #             # 'freight_item_qty': self.freight_item_qty,
    #             'freight_container_type': rec.freight_container_type,
    #             'freight_teus20ft': rec.freight_teus20ft,
    #             'freight_ffe40ft': rec.freight_ffe40ft,
    #             'freight_etd': rec.freight_etd,
    #             'rate_validity': rec.rate_validity,
    #             'rate_in_foreign_currency': rec.rate_in_foreign_currency,
    #             'amount_in_foreign_currency': rec.amount_in_foreign_currency,
    #             'foreign_currency': rec.foreign_currency,
    #
    #         }
    #         if optional_values:
    #             res.update(optional_values)
    #         if self.display_type:
    #             res['account_id'] = False
    #         self.invoice_line_ids.create(res)

class CustomerQuotation(models.Model):
    _inherit = 'sale.order'
    freight_operation_ids = fields.One2many('freight.operation','quotation_id',string='Freight ID')

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                # 'default_freight_operation_id': self.freight_operation_id.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action
    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            invoice_lines_vals = []
            for line in order.order_line:
                if line.display_type == 'line_section':
                    current_section_vals = line._prepare_invoice_line(sequence=invoice_item_sequence + 1)
                    continue
                if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                    if line.is_downpayment:
                        down_payments += line
                        continue
                    if current_section_vals:
                        invoice_item_sequence += 1
                        invoice_lines_vals.append(current_section_vals)
                        current_section_vals = None
                    invoice_item_sequence += 1
                    prepared_line = line._prepare_invoice_line(sequence=invoice_item_sequence)
                    invoice_lines_vals.append(prepared_line)

            # If down payments are present in SO, group them under common section
            if down_payments:
                invoice_item_sequence += 1
                down_payments_section = order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                invoice_lines_vals.append(down_payments_section)
                for down_payment in down_payments:
                    invoice_item_sequence += 1
                    invoice_down_payment_vals = down_payment._prepare_invoice_line(sequence=invoice_item_sequence)
                    invoice_lines_vals.append(invoice_down_payment_vals)

            if not any(new_line['display_type'] is False for new_line in invoice_lines_vals):
                raise self._nothing_to_invoice_error()

            invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_id) for invoice_line_id in invoice_lines_vals]

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    # 'freight_operation_id': self.freight_operation_id.id,
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves

class ShipmentStage(models.Model):
    _name = 'shipment.stage'
    _description = 'shipment Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

class FreightRateBasis(models.Model):
    _name ="freight.rate.basis"
    name=fields.Char("Name")
    details=fields.Char("Details")

class FreightContainerType(models.Model):
    _name ="freight.container.type"
    name=fields.Char("Container Type")
    description=fields.Char("Descriptiion")
class FreightContainerSize(models.Model):
    _name ="freight.container.size"
    name=fields.Char("Cont. size")
    description=fields.Char("Descriptiion")

class FreightOperationContainers(models.Model):
    _name = 'freight.operation.containers'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Freight Operation containers for job/Operation'
    # name=fields.Char("Container")
    operation_id = fields.Many2one('freight.operation', string='Operation ID')
    container_size=fields.Many2one("freight.container.size", string="Cont.Size")
    container_type=fields.Many2one("freight.container.type")
    qty=fields.Float("Cont.Qty")

    # Todo here to calculate operation lines qty for container qty
    @api.onchange('qty')
    def qty_onchange(self):
        jobLines=self.operation_id.freight_line_ids
        containerLines=self.operation_id.freight_operation_containers
        values= {}
        values['totalQty']=0
        for cont in containerLines:
            if cont.container_type.name and cont.container_type.name  not in values.keys():
                values[cont.container_type.name]={}
                values[cont.container_type.name]["total"]=0
                if cont.container_size:
                    values[cont.container_type.name][cont.container_size.name]=0
            if cont.container_size.name and cont.container_size.name not in values.keys():
                values[cont.container_size.name] = {}
                values[cont.container_size.name]["total"]=0
                if cont.container_type:
                    values[cont.container_size.name][cont.container_type.name]=0
                    values[cont.container_type.name][cont.container_size.name]=0
            values['totalQty']=values['totalQty']+cont.qty
            if cont.container_type and cont.container_size:
                values[cont.container_type.name][cont.container_size.name]=values[cont.container_type.name][cont.container_size.name]+cont.qty
                values[cont.container_size.name][cont.container_type.name]=values[cont.container_size.name][cont.container_type.name]+cont.qty
                values[cont.container_type.name]["total"]=values[cont.container_type.name]["total"]+cont.qty
                values[cont.container_size.name]["total"]=values[cont.container_size.name]["total"]+cont.qty
            elif cont.container_type:
                values[cont.container_type.name]["total"] = values[cont.container_type.name]["total"] + cont.qty
            elif cont.container_size:
                values[cont.container_size.name]["total"] = values[cont.container_size.name]["total"] + cont.qty

        for job in jobLines:
            if job.rate_basis == self.env.ref('freight.freight_rate_basis_container'):
                # here to update product_uom of freight.opration.line
                if job.freight_container_type and job.container_size:
                   job._origin.product_uom_qty=values[job.freight_container_type.name][job.container_size.name]
                elif job.container_size:
                    job._origin.product_uom_qty=values[job.container_size.name]["total"]
                elif job.freight_container_type:
                    job._origin.product_uom_qty=values[job.freight_container_type.name]["total"]
                else:
                    job._origin.product_uom_qty = values["totalQty"]
            else:
                job._origin.product_uom_qty = 1
                # job._origin.qty_onchange()
                # self.env['freight.operation.line'].browse(job._origin.id).product_uom_qty=values[job.freight_container_type.name][job.container_size.name]



class FreightOperation(models.Model):
    _name = 'freight.operation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Freight Operation'


    def _get_default_stage_id(self):
        return self.env['shipment.stage'].search([], order='sequence', limit=1)


    color = fields.Integer('Color')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    client_order_ref=fields.Char("Ref")
    reference = fields.Char('Reference')
    payment_term_id = fields.Many2one('account.payment.term', 'Terms of Payment')
    stage_id = fields.Many2one('shipment.stage', 'Stage',default=_get_default_stage_id, group_expand='_read_group_stage_ids')
    name = fields.Char(string='Name', copy=False)
    direction = fields.Selection(([('import','Import'),('export','Export'),('crosstrade','Crosstrade')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Customer')
    consignee_id = fields.Many2one('res.partner', 'Vendor')
    source_location_id = fields.Many2one('freight.port', 'POL', index=True)
    source_flag_url = fields.Char("Flag", related="source_location_id.country.image_url")
    destination_flag_url = fields.Char("Flag", related="destination_location_id.country.image_url")
    country_id = fields.Many2one('res.country', 'Country')
    destination_location_id = fields.Many2one('freight.port', 'POD', index=True)
    bill_of_ladding = fields.Char('BL', help='Original Bill Of Landing')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_number = fields.Char('Trucker No')
    agent_id = fields.Many2one('res.partner', 'Agent')
    operator_id = fields.Many2one('res.users', 'User')
    freight_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Freight PC")
    other_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Other PC")
    notes = fields.Text('Notes')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    dangerous_goods_notes = fields.Text('Dangerous Goods Info')
    move_type = fields.Many2one('freight.move.type', 'Move Type')
    tracking_number = fields.Char('Tracking Number')
    declaration_number = fields.Char('Declaration Number')
    declaration_date = fields.Date('Declaration Date')
    custom_clearnce_date = fields.Datetime('Customs Clearance Date')
    freight_orders = fields.One2many('freight.order', 'shipment_id')
    freight_packages = fields.One2many('freight.package.line', 'shipment_id')
    freight_services = fields.One2many('freight.service', 'shipment_id')
    incoterm = fields.Many2one('freight.incoterms','Incoterm')
    freight_routes = fields.One2many('freight.route', 'shipment_id')
    parent_id = fields.Many2one('freight.operation', 'Parent')
    shipments_ids = fields.One2many('freight.operation', 'parent_id')
    quotation_count = fields.Float('Quotation Count', compute='_compute_invoice')
    service_count = fields.Float('Services Count', compute='_compute_invoice')
    invoice_count = fields.Float('Services Count', compute='_compute_invoice')
    vendor_bill_count = fields.Float('Services Count', compute='_compute_invoice')
    total_invoiced = fields.Float('Total Invoiced(Receivables', compute='compute_total_amount')
    total_bills = fields.Float('Total Bills(Payables)', compute='compute_total_amount')
    button_sale_quote_to_freight = fields.Char('Creare Freight')
    margin = fields.Float("Margin", compute='compute_total_amount')
    invoice_residual = fields.Float('Invoice Residual',compute='compute_total_amount')
    bills_residual = fields.Float('Bills Residual', compute='compute_total_amount')
    invoice_paid_amount = fields.Float('Invoice', compute='compute_total_amount')
    bills_paid_amount = fields.Float('Bills', compute='compute_total_amount')
    actual_margin = fields.Float('Actual Margin', compute='compute_total_amount')

    freight_month = fields.Selection([('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'),
                              ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
                              ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')],
                             string='Month')
    freight_bill_of_ladding = fields.Char("Bill of Ladding")
    freight_container_no = fields.Char("Container No.")
    freight_booking_no = fields.Char("Booking No.")

    # port_of_loading = fields.Many2one('freight.port', string="POL", store=True)
    # port_of_delivery = fields.Many2one('freight.port', string="POD", store=True)
    freight_etd = fields.Date("ETD")
    freight_eta = fields.Date("ETA")
    # quotation_ids = fields.Many2many('sale.order',"freight_operation_sale_order_rel","freight_operation_ids","quotation_ids", string='Quotation')
    quotation_id = fields.Many2one('sale.order', string='Quotation')

    freight_sales_person = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, tracking=True)
    freight_service = fields.Char("Service")
    freight_ts = fields.Char("T/S")
    # project_status = fields.Selection([('pending', 'Pending'), ('cancelled', 'Cancelled'), ('booked', 'Booked'), ('sailed', 'Sailed')], string='Status', default='pending')
    freight_status = fields.Many2one('freight.status', string='Status')
    freight_dostatus = fields.Many2one('freight.dostatus', string='DO Status')
    freight_dovalidity = fields.Date(string='DO Validity')
    freight_item_qty = fields.Integer("Volume (Qty)")
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    # freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #         ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', default='2000', store=True)
    freight_teus20ft = fields.Float(string="TEUS (20ft)", digits=(12,1), readonly=True)
    freight_ffe40ft = fields.Float(string="FFE (40ft)", digits=(12,1), readonly=True)
    freight_validity = fields.Date("Quote Validity")
    freight_carier = fields.Char("Carier")
    freight_billofentry = fields.Many2one('freight.billofentry', string='BOE')
    freight_si_submitted = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled'), ('done', 'Done')], string='SI Submitted', default='no')
    freight_vgm = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='VGM', default='no')
    freight_bl_draft = fields.Selection([('yes', 'Yes'),('no', 'No'), ('sent_to_customer', 'Sent to Customer'), ('approved', 'Approved'), ('cancelled', 'Cancelled')], string='BL Draft', default='no')
    freight_swb = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='SWB', default='no')
    freight_invoice = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='Invoice', default='no')
    freight_remarks = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'), ('sent_to_customer', 'Sent to Customer'), ('sent_to_carrier', 'Sent to Carrier')], string='Remarks', default='pending')
    freight_project_manager = fields.Many2one('res.users', 'Project Manager')
    freight_line_ids = fields.One2many('freight.operation.line', 'operation_id')
    freight_service_line_ids = fields.One2many('freight.service.line', 'operation_id')

    freight_operation_containers=fields.One2many("freight.operation.containers",'operation_id')



    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.notes,
            'currency_id': self.shipper_id.currency_id.id,
            # 'campaign_id': self.campaign_id.id,
            # 'medium_id': self.medium_id.id,
            # 'source_id': self.id,
            'freight_operation_id': self.id,
            'invoice_user_id': self.env.user.id,
            # 'team_id': self.team_id.id,
            'partner_id': self.shipper_id.id,
            # 'partner_shipping_id': self.partner_shipping_id.id,
            # 'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            # 'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            # 'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals

    def _get_invoice_grouping_keys(self):
        return ['company_id', 'partner_id', 'currency_id']
    # def create_inventory_transactions(self):
    #     for rec in self:
    #         picking_data={
    #             'partner_id': rec.shipper_id.id,
    #             #todo set picking_type_id
    #             # 'picking_type_id':
    #         }
    #         picking=self.env['stock.picking'].create(picking_data)
    #         for line in rec.move_ids_without_package:
    #             move_data = {
    #                 'picking_id': picking.id,
    #                 'product_id': line.product.id,
    #                 # TODO get location_id and location_dest here
    #                 # 'location_id': location_id.id,
    #                 # 'location_dest_id': location_dest_id.id,
    #                 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #                 'date_expected': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #                 'name': line.product.name,
    #                 'procure_method': 'make_to_stock',
    #                 'product_uom': line.product.uom_id.id,
    #                 'product_uom_qty': 1.0,
    #                 'analytic_account_id': analytic_account_id and
    #                                        analytic_account_id.id or False
    #             }
    #             move=self.env['stock.move'].create(move_data)

    def create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            invoice_lines_vals = []
            for line in order.freight_line_ids:
                if line.selected:
                    if line.product_uom_qty > 0:
                        invoice_item_sequence += 1
                        prepared_line = line._prepare_invoice_line(sequence=invoice_item_sequence)
                        invoice_lines_vals.append(prepared_line)

            ## create freight_invoice containers here
            invoice_continer_vals = []
            for line in order.freight_operation_containers:
                if line.qty>0:
                    vals={}
                    vals["container_type"]=line.container_type.id
                    vals["container_size"]=line.container_size.id
                    vals["qty"]=line.qty
                    invoice_continer_vals.append(vals)

            invoice_vals['freight_container_lines'] = [(0, 0, invoice_conainer_line_id) for invoice_conainer_line_id in invoice_continer_vals]
            invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_id) for invoice_line_id in invoice_lines_vals]

            freight_move_group_vals=order.prepare_freight_invoice_groups()
            invoice_vals['freight_move_group_ids'] = [(0, 0, freight_move_group_id) for freight_move_group_id in freight_move_group_vals]

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list,
                                                   key=lambda x: [x.get(grouping_key) for grouping_key in
                                                                  invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    # 'freight_operation_id': self.freight_operation_id.id,
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                                        values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                                        subtype_id=self.env.ref('mail.mt_note').id
                                        )
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            # action['domain'] = [('id', '=', move.id)]
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            action['views'] = form_view
            action['res_id'] = move.id
            return action

    def prepare_freight_invoice_groups(self):
        freightInvoiceGroup_vals=[]
        freight_group_lines={}
        for line in self.freight_line_ids:
            pol=line.port_of_loading
            pod=line.port_of_delivery
            portSet= pol.name+pod.name
            if portSet not in freight_group_lines.keys():
                freight_group_lines[portSet]= {}
            chargeType=line.product_id.charge_type
            if chargeType.name not in freight_group_lines[portSet].keys():
                freight_group_lines[portSet][chargeType.name]={}
                freight_group_lines[portSet][chargeType.name]['id']=chargeType

            size=line.container_size
            if size not in freight_group_lines[portSet][chargeType.name].keys():
                freight_group_lines[portSet][chargeType.name][size]=line.product_uom_qty
        freight_invoicegroups=[]
        for rec in freight_group_lines:
            group_vals={}
            group_vals["charge_type_id"]=freight_group_lines[rec]["Main Carrier Charges"]['id']



        return freight_invoicegroups



    @api.onchange('freight_item_qty', 'freight_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.freight_teus20ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 2000
            rec.freight_ffe40ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 4000


    @api.depends('freight_services')
    def compute_total_amount(self):
        for order in self:
            invoices = self.env['account.move'].sudo().search([('freight_operation_id', '=', order.id), ('move_type', '=', 'out_invoice')])
            invoice_amount = 0.0
            bill_amount = 0.0
            invoice_residual = 0.0
            bills_residual = 0.0
            for invoice in invoices:
                invoice_amount+=invoice.amount_total
                invoice_residual+= invoice.amount_residual

            bills = self.env['account.move'].sudo().search([('freight_operation_id', '=', order.id), ('move_type', '=', 'in_invoice')])
            for bill in bills:
                bill_amount+=bill.amount_total
                if bill.state != 'draft':
                    bills_residual+= bill.amount_residual

            order.total_invoiced = invoice_amount
            order.total_bills = bill_amount
            order.margin =  invoice_amount - bill_amount
            order.invoice_residual = invoice_residual
            order.bills_residual = bills_residual

            payment_total = 0.0
            for invoice in invoices:
                payment_ids = self.env['account.move'].sudo().search(
                    [('ref', '=', invoice.name), ('move_type', '=', 'entry')])

                for payment in payment_ids:
                    payment_total+=payment.amount_total
            order.invoice_paid_amount = payment_total
            bill_payment_total = 0.0
            for bill_payment in bills:
                bill_payment_ids = self.env['account.move'].sudo().search(
                    [('ref', '=', bill_payment.name), ('move_type', '=', 'entry')])
                for bill_payment_id in bill_payment_ids:
                    bill_payment_total+=bill_payment_id.amount_total
            order.bills_paid_amount = bill_payment_total
            order.actual_margin =order.invoice_paid_amount - order.bills_paid_amount


    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['shipment.stage'].search([])
        return stage_ids

    @api.depends('freight_services')
    def _compute_invoice(self):
        for order in self:
            order.service_count = len(order.freight_services)
            order.invoice_count = self.env['account.move'].sudo().search_count([('freight_operation_id','=', order.id),('move_type','=', 'out_invoice')])
            # order.sale_order_count = self.env['sale.order'].sudo().search_count([('freight_operation_id','=', order.id),('move_type','=', 'out_invoice')])
            order.vendor_bill_count  = self.env['account.move'].sudo().search_count([('freight_operation_id','=', order.id),('move_type','=', 'in_invoice')])
            order.quotation_count = self.env['sale.order'].sudo().search_count([('freight_operation_ids', '=', order.id)])

    #@api.multi
    def button_services(self):
        views = [(self.env.ref('freight.view_freight_service_tree').id, 'tree'),
                 (self.env.ref('freight.view_freight_service_form').id, 'form')]
        return {
            'name': _('Services'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'freight.service',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'context': {'default_route_id' : self.freight_routes.id},
            'domain': [('id', 'in', [x.id for x in self.freight_services])],
        }

    def button_quotation(self):
        views = [(self.env.ref('sale.view_quotation_tree_with_onboarding').id, 'tree'),
                 (self.env.ref('sale.view_order_form').id, 'form')]

        return {
            'name': _('Quotation'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'context': {'default_partner_id': self.shipper_id.id,
                'default_freight_operation_ids': [(6,0,self.ids)]
            },
            'domain': [('freight_operation_ids', '=', self.id)],
        }

    def button_customer_invoices(self):
        invoices = self.env['account.move'].sudo().search(
                    [('freight_operation_id', '=', self.id), ('move_type', '=', 'out_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.consignee_id.id,
                'default_partner_shipping_id': self.consignee_id.id,
                'default_invoice_payment_term_id':  self.consignee_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_freight_operation_id': self.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self._context['uid'],
            })
        action['context'] = context
        return action

    #@api.multi
    def button_vendor_bills(self):
        invoices = self.env['account.move'].sudo().search(
            [('freight_operation_id', '=', self.id), ('move_type', '=', 'in_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

        context = {
            'default_move_type': 'in_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.consignee_id.id,
                'default_partner_shipping_id': self.shipper_id.id,
                'default_invoice_payment_term_id': self.shipper_id.property_supplier_payment_term_id.id or self.env[
                    'account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_freight_operation_id': self.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self._context['uid'],
            })
        action['context'] = context
        return action
    #
    # @api.model
    # def create(self, vals):
    #     vals['default_code'] = self.env['ir.sequence'].next_by_code('product.code') or _('New')
    #     return super(ClassName, self).create(vals)


    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):

            # if values.get('freight_serial_no', _('New')) == _('New'):
            #     values['freight_serial_no'] = self.env['ir.sequence'].next_by_code('freight.operation.sequence') or _('New')

            if values.get('operation') == 'master':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.master') or _('New')
            elif values.get('operation') == 'house':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.house') or _('New')
            elif values.get('operation') == 'direct':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.direct') or _('New')
        id = super(FreightOperation, self).create(values)
        if id.transport == 'air':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'mawb_no': id.mawb_no,
                                              'airline_id': id.airline_id.id,
                                              'flight_no': id.flight_no,
                                              'shipment_id': id.id})
        if id.transport == 'ocean':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'shipping_line_id': id.shipping_line_id.id,
                                              'vessel_id': id.vessel_id.id,
                                              'bill_of_ladding': id.bill_of_ladding,
                                              'shipment_id': id.id})
        if id.transport == 'land':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'truck_ref': id.truck_ref,
                                              'trucker': id.trucker.id,
                                              'trucker_number': id.trucker_number,
                                              'shipment_id': id.id})

        return id


    @api.depends('transport')
    @api.onchange('source_location_id')
    def onchange_source_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'source_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'source_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'source_location_id': [('land', '=', True)]}}

    @api.depends('transport')
    @api.onchange('destination_location_id')
    def onchange_destination_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'destination_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'destination_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'destination_location_id': [('land', '=', True)]}}

    #@api.multi
    def generate_from_the_orders(self):
        for line in self:
            packages = []
            for order in line.freight_orders:
                packages.append((0, 0, {'name': order.name,
                                        'package':order.package.id,
                                        'qty': order.qty,
                                        'volume': order.volume,
                                        'gross_weight': order.gross_weight,
                                        'shipment_id':line.id}))
            self.freight_packages.unlink()
            self.write({'freight_packages':packages})

class FreightOperationLine(models.Model):
    _name = 'freight.operation.line'
    _description = 'Freight Operation Line'

    selected = fields.Boolean("Select", default="False")
    sale_order_id = fields.Many2one('sale.order', 'Sale Order Id')
    operation_id = fields.Many2one('freight.operation', string='Operation ID')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one('uom.uom', 'Unit')
    rate_basis = fields.Many2one("freight.rate.basis")
    port_of_loading = fields.Many2one('freight.port', string="POL")
    port_of_delivery = fields.Many2one('freight.port', string="POD")
    container_size=fields.Many2one("freight.container.size",string='Size')
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    # freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #         ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type')
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1))
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1))
    freight_etd = fields.Date(string='ETD')
    rate_validity = fields.Date(string='Rate Validity')
    freight_item_qty = fields.Integer("Vol. Qty", store=True)
    price_unit = fields.Float('Unt Rate (AED)')
    price_subtotal = fields.Float('Amount (AED)',compute='qty_onchange')
    product_uom_qty = fields.Float('Qty', default="1")
    foreign_currency = fields.Many2one('res.currency', string='Curr.', store=True,
                                       default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate', compute='qty_onchange')

    rate_in_foreign_currency = fields.Float(string='Rate Forex')
    amount_in_foreign_currency = fields.Float(string='Amt. Fo', compute='qty_onchange')

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.product_uom_qty,
            'price_unit': self.price_unit,
            'rate_basis': self.rate_basis,
            'port_of_loading': self.port_of_loading,
            'port_of_delivery': self.port_of_delivery,
            'freight_container_size': self.container_size,
            'freight_container_type': self.freight_container_type,
            'freight_teus20ft': self.freight_teus20ft,
            'freight_ffe40ft': self.freight_ffe40ft,
            'freight_etd': self.freight_etd,
            'rate_validity': self.rate_validity,
            'rate_in_foreign_currency': self.rate_in_foreign_currency,
            'amount_in_foreign_currency': self.amount_in_foreign_currency,
            'foreign_currency': self.foreign_currency,
        }
        if optional_values:
            res.update(optional_values)
        # if self.display_type:
        #     res['account_id'] = False
        return res


    # @api.onchange('product_id','product_uom','product_uom_qty')
    # def calculate_prices(self):
    #     for rec in self:
    #         rec.price_unit = rec.product_id.with_context(
            #     pricelist=self.operation_id.quotation_id.partner_id.property_product_pricelist.id).price
            # rec.price_subtotal = rec.price_unit * rec.product_uom_qty

    # @api.onchange('price_unit')
    # def price_unit_on_change(self):
    #     for rec in self:
    #         rec.price_subtotal = rec.price_unit * rec.product_uom_qty

    @api.onchange('product_uom_qty','foreign_currency','price_unit','product_id','product_uom','product_uom_qty','rate_in_foreign_currency')
    def qty_onchange(self):
        for rec in self:
            rec.ex_currency_rate = 1 / rec.foreign_currency.rate
            rec.price_unit = rec.rate_in_foreign_currency * rec.ex_currency_rate
            rec.price_subtotal = rec.price_unit * rec.product_uom_qty
            rec.amount_in_foreign_currency = rec.rate_in_foreign_currency * rec.product_uom_qty
            rec.price_subtotal = rec.price_unit * rec.product_uom_qty


class FreightServiceLine(models.Model):
    _name = 'freight.service.line'
    _description='Freight Service order Line'

    selected=fields.Boolean("Select",default="False")
    sale_order_id = fields.Many2one('sale.order', 'Sale Order Id')
    operation_id = fields.Many2one('freight.operation', string='Operation ID')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one('uom.uom', 'Unit')
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Float('Sub Total')
    product_uom_qty = fields.Float('Qty', default="1")

    port_of_loading = fields.Many2one('freight.port', string="POL", store=True)
    port_of_delivery = fields.Many2one('freight.port', string="POD", store=True)
    freight_item_qty = fields.Integer("Vol. Qty", store=True)
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    # freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #         ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', store=True)
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1), store=True)
    freight_etd = fields.Date(string='ETD', store=True)
    rate_validity = fields.Date(string='Rate Validity', store=True)

    foreign_currency = fields.Many2one('res.currency', string='Currency', store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate')

    rate_in_foreign_currency = fields.Float(string='Rate Forex', compute='_compute_currency', inverse='_inverse_price_unit')
    amount_in_foreign_currency = fields.Float(string='Amt. Forex', compute='_compute_currency')

    # @api.onchange('rate_in_foreign_currency')
    # def _compute_ex_currency(self):
    #     for rec in self:
    #         rec.ex_currency_rate = 1 / rec.foreign_currency.rate

    @api.onchange('rate_in_foreign_currency')
    def _inverse_price_unit(self):
        for rec in self:
            # rec.rate_in_foreign_currency = rec.price_unit * rec.foreign_currency.rate
            rec.price_unit = rec.rate_in_foreign_currency /rec.foreign_currency.rate
            rec.amount_in_foreign_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    @api.onchange('foreign_currency', 'price_unit', 'product_uom_qty')
    def _compute_currency(self):
        for rec in self:
            rec.rate_in_foreign_currency = rec.price_unit * rec.foreign_currency.rate
            rec.amount_in_foreign_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    @api.onchange('product_id','product_uom','product_uom_qty')
    def calculate_prices(self):
        for rec in self:
            rec.price_unit = rec.product_id.with_context(
                pricelist=self.operation_id.quotation_id.partner_id.property_product_pricelist.id).price
            rec.price_subtotal=rec.price_unit*rec.product_uom_qty

    @api.onchange('price_unit')
    def calculate_subtotal(self):
        for rec in self:
            rec.price_subtotal=rec.price_unit*rec.product_uom_qty


    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            # 'display_type': self.display_type,
            # 'sequence': self.sequence,
            # 'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.product_uom_qty,
            # 'discount': self.discount,
            'price_unit': self.price_unit,
            # 'tax_ids': [(6, 0, self.tax_id.ids)],
            # 'analytic_account_id': self.order_id.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            # 'sale_line_ids': [(4, self.id)],
            'port_of_loading': self.port_of_loading,
            'port_of_delivery': self.port_of_delivery,

            # 'freight_item_qty': self.freight_item_qty,
            'freight_container_type': self.freight_container_type,
            'freight_teus20ft': self.freight_teus20ft,
            'freight_ffe40ft': self.freight_ffe40ft,
            'freight_etd': self.freight_etd,
            'rate_validity': self.rate_validity,
            'rate_in_foreign_currency': self.rate_in_foreign_currency,
            'amount_in_foreign_currency': self.amount_in_foreign_currency,
            'foreign_currency': self.foreign_currency,

        }
        if optional_values:
            res.update(optional_values)
        # if self.display_type:
        #     res['account_id'] = False
        return res

########################################## job to invoice line ##########################



########################################## job to invoice line ##########################



class FreightTrucker(models.Model):
    _name = 'freight.trucker'

    name = fields.Char(string='Name')

class FreightPackageLine(models.Model):
    _name = 'freight.package.line'

    name = fields.Char(string='Description', required=True)
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity', required=True)
    harmonize = fields.Char('Harmonize')
    temperature = fields.Char('Temperature')
    vgm = fields.Char('VGM', help='Verified gross mass')
    carrier_seal = fields.Char('Carrier Seal')
    shipper_seal = fields.Char('Customer Seal')
    reference = fields.Char('Reference')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    class_number = fields.Char('Class Number')
    un_number = fields.Char('UN Number', help='UN numbers are four-digit numbers that identify hazardous materials, and articles in the framework of international transport')
    Package_group = fields.Char('Packaging Group:')
    imdg_code = fields.Char('IMDG Code', help='International Maritime Dangerous Goods Code')
    flash_point = fields.Char('Flash Point')
    material_description = fields.Text('Material Description')
    freight_item_lines = fields.One2many('freight.item.line', 'package_line_id')
    route_id = fields.Many2one('freight.route', 'Route')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightItemLine(models.Model):
    _name = 'freight.item.line'

    name = fields.Char(string='Description')
    package_line_id = fields.Many2one('freight.package.line', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package')
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.package_line_id.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightOrder(models.Model):
    _name = 'freight.order'

    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    name = fields.Char(string='Description', required=True)
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightService(models.Model):
    _name = 'freight.service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Paying')
    sale = fields.Float('Selling')
    qty = fields.Float('Quantity')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    route_id = fields.Many2one('freight.route', 'Route')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID', related='route_id.shipment_id')
    customer_invoice = fields.Many2one('account.move')
    vendor_invoice = fields.Many2one('account.move')
    invoiced = fields.Boolean('Invoiced')
    vendor_invoiced = fields.Boolean('Vendor Invoiced')

    # todo
    # roni = fields.One2many(...
    # another_field = fields.Float(string="Actual Total", compute='_compute_total')

    # @api.depends('freight.service')


    # def _amount_total(self):
    #     for rec in self:
    #         total = sum(rec.total_service_selling.mapped('cost')) if rec.total_service_selling else 0
    #         rec.total_amount = total





# class FreightService(models.Model):
#     _name = 'freight.service'
#     _inherit = 'product.product'
#
#     service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
#     # currency_id = fields.Many2one('res.currency', 'Currency')
#     # name = fields.Char(string='Description')
#     # cost = fields.Float('Cost')
#     # sale = fields.Float('Sale')
#     # qty = fields.Float('Quantity')
#     # partner_id = fields.Many2one('res.partner', 'Vendor')
#     # route_id = fields.Many2one('freight.route', 'Route')
#     # shipment_id = fields.Many2one('freight.operation', 'Shipment ID', related='route_id.shipment_id')
#     # customer_invoice = fields.Many2one('account.move')
#     # vendor_invoice = fields.Many2one('account.move')
#     # invoiced = fields.Boolean('Invoiced')
#     # vendor_invoiced = fields.Boolean('Vendor Invoiced')



class FreightRoute(models.Model):
    _name = 'freight.route'

    name=fields.Char('Description', compute='compute_name')
    type = fields.Selection([('pickup', 'Pickup'), ('oncarriage', 'On Carriage'), ('precarriage', 'Pre Carriage'),('delivery', 'Delivery')], string='Type')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection([('air','Air'),('ocean','Ocean'),('land','Land')], string='Transport')
    ocean_shipment_type = fields.Selection([('fcl','FCL'),('lcl','LCL')], string='Shipment Type')
    inland_shipment_type = fields.Selection([('ftl','FTL'),('ltl','LTL')], string='Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Customer')
    consignee_id = fields.Many2one('res.partner', 'Vendor/Consignee')
    source_location_id = fields.Many2one('freight.port', 'POL')
    destination_location_id = fields.Many2one('freight.port', 'POD')
    bill_of_ladding = fields.Char('BL', help='Bill Of Lading')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_number = fields.Many2one('freight.trucker', 'Trucker No')
    etd = fields.Datetime('ETD')
    eta = fields.Datetime('ETA')
    atd = fields.Datetime('ATD')
    ata = fields.Datetime('ATA')
    package_ids = fields.One2many('freight.package.line', 'route_id')
    freight_services = fields.One2many('freight.service', 'route_id')
    main_carriage = fields.Boolean('Main Carriage',default="True")

    @api.model
    def create(self, values):
        id = super(FreightRoute, self).create(values)
        id.freight_services.write({'shipment_id':id.shipment_id})
        return id

    #@api.multi
    def compute_name(self):
        for line in self:
            if line.main_carriage:
                line.name = 'Main carriage'
            elif line.type:
                line.name = line.type

    @api.onchange('type')
    def onchange_type(self):
        for line in self:
            if line.type == 'precarriage':
                line.destination_location_id = line.shipment_id.source_location_id
            if line.type == 'oncarriage':
                line.source_location_id = line.shipment_id.destination_location_id

class FreightRouteService(models.Model):
    _name = 'freight.route.service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    partner_id = fields.Many2one('res.partner', 'Vendor')




class FreightPort(models.Model):
    _name = 'freight.port'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    country = fields.Many2one('res.country', 'Country')
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=', country)]")
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')
    active = fields.Boolean(default=True, string='Active')

class FreightVessel(models.Model):
    _name = 'freight.vessel'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    global_zone = fields.Char(string='Global Zone')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightAirline(models.Model):
    _name = 'freight.airline'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    icao = fields.Char(string='ICAO')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightIncoterms(models.Model):
    _name = 'freight.incoterms'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name',  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    active = fields.Boolean(default=True, string='Active')

class FreightPackage(models.Model):
    _name = 'freight.package'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    container = fields.Boolean('Is Container?')
    refrigerated = fields.Boolean('Refrigerated')
    active = fields.Boolean(default=True, string='Active')
    size = fields.Float('Size')
    volume = fields.Float('Volume')
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')

class FreightMoveType(models.Model):
    _name = 'freight.move.type'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')

class SaleAdvancePaymentInvoice(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            # 'freight_operation_id': order.freight_operation_id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals

class FreightCurrencyrate(models.Model):
    _name = 'freight.currencyrate'
    _description = 'Freight Currency Rate'
    _rec_name = 'currency_name'

    currency_name=fields.Char('Currency Name')
    currency_rate=fields.Float('Currency rate', digits = (12,6))


class resCountry(models.Model):
    _name = "res.country.flag"
    _description = "show flag for country"

    country_id=fields.Many2one('res.country',"country")
    flag=fields.Binary('Flag', compute='get_flag')
    test=fields.Binary("test")

    @api.onchange('country_id')
    def get_flag(self):
        image=False
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if rec.country_id:
                image_url=base_url+"/base/static/img/country_flags/"+rec.country_id.code +".png"
                image=base64.encodestring(urllib.request.urlopen(image_url).read())
            rec.flag=image


class FreightStatus(models.Model):
    _name = "freight.status"
    _description = "Status"
    name = fields.Char(string="Status")

class FreightDostatus(models.Model):
    _name = "freight.dostatus"
    _description = "Status"
    name = fields.Char(string="DO Status")

class FreightBillofentry(models.Model):
    _name = "freight.billofentry"
    _description = "Status"
    name = fields.Char(string="BOE")

