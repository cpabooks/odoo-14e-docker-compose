# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class QuotationInherit(models.Model):
    _inherit = "sale.order"

    direction = fields.Selection(([('import', 'Import'), ('export', 'Export'), ('crosstrade', 'Crosstrade')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    comodity = fields.Char('Comodity')
    service_line=fields.One2many("quotation.service.line", 'sale_order_id')

    def _prepare_invoice(self):
        res = super(QuotationInherit, self)._prepare_invoice()
        res['direction'] = self.direction
        res['transport'] = self.transport
        res['operation'] = self.operation
        res['ocean_shipment_type'] = self.ocean_shipment_type
        res['inland_shipment_type'] = self.inland_shipment_type
        return res


    def create_freight_job(self):
        for rec in self:
            values = {
                # 'name': rec.id,
                'direction': rec.direction,
                'transport': rec.transport,
                'ocean_shipment_type': rec.ocean_shipment_type,
                'inland_shipment_type': rec.inland_shipment_type,
                'shipper_id': rec.partner_id.id,
                'datetime': rec.date_order,
                'operation': 'direct',
                'quotation_id': rec.id
            }

            freight = self.env['freight.operation'].create(values)
            # rec.freight_operation_id=(4,freight.id)
            container_types= []
            for line in self.order_line:
                if line.selected :
                    if line.freight_container_type.id not in container_types:
                        container_types.append(line.freight_container_type.id)

                    line_vals = {
                    'operation_id': freight.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_uom": line.product_uom.id,
                    "port_of_loading": line.port_of_loading.id,
                    "port_of_delivery": line.port_of_delivery.id,
                    "rate_basis": line.rate_basis.id,
                    "freight_container_type": line.freight_container_type.id,
                    "freight_teus20ft": line.freight_teus20ft,
                    "freight_ffe40ft": line.freight_ffe40ft,
                    "freight_etd": line.freight_etd,
                    "rate_validity": line.rate_validity,
                    "foreign_currency": line.foreign_currency.id,
                    "ex_currency_rate": line.ex_currency_rate,
                    # "rate_as_currency": line.rate_as_currency,
                    # "amount_as_currency": line.amount_as_currency,
                    # "price_unit": line.price_unit,
                    # "price_subtotal": line.price_subtotal,
                }
                    containerSizes=self.env['freight.container.size'].search([('id','>',0)])
                    if line.product_id.charge_type.id==self.env.ref('freight_in_quotation.freight_charge_type_main').id:
                        for val in containerSizes:
                            line_vals['container_size']=val.id
                            if val.id==1:
                                line_vals['rate_as_currency']=line['freight_20ge']
                            elif val.id==2:
                                line_vals['rate_as_currency'] = line['freight_40ge']
                            elif val.id==3:
                                line_vals['rate_as_currency'] = line['freight_40hc']
                            freight_line = self.env['freight.operation.line'].create(line_vals)
                    else:
                        line_vals['rate_as_currency'] = line['freight_20ge']
                        freight_line = self.env['freight.operation.line'].create(line_vals)
            for rec in container_types:
                if rec:
                    for containers in self.env['freight.container.size'].search([('id','>',0)]):
                        vals = {}
                        vals["operation_id"]=freight.id
                        vals["container_type"]=rec
                        vals['container_size']=containers.id
                        self.env['freight.operation.containers'].create(vals)

            for line in self.service_line:
                if line.selected:
                    line_vals_service = {
                    'operation_id': freight.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_uom": line.product_uom.id,
                    "port_of_loading": line.port_of_loading.id,
                    "port_of_delivery": line.port_of_delivery.id,
                    # "freight_item_qty": line.freight_item_qty,
                    "freight_container_type": line.freight_container_type,
                    "freight_teus20ft": line.freight_teus20ft,
                    "freight_ffe40ft": line.freight_ffe40ft,
                    "freight_etd": line.freight_etd,
                    "rate_validity": line.rate_validity,
                    "foreign_currency": line.foreign_currency.id,
                    "rate_as_currency": line.rate_as_currency,
                    "ex_currency_rate": line.ex_currency_rate,
                    "amount_as_currency": line.amount_as_currency,
                    "price_unit": line.price_unit,
                    "price_subtotal": line.price_subtotal,
                }
                    service_line = self.env['freight.service.line'].create(line_vals_service)

            # self.created_job=freight.id
            # rec.write({
            #     'state': 'sent'
            # })

            return {
                # 'name': _('Job Name'),
                'view_type': 'form',
                'view_mode': 'form',
                # 'view_id': 'freight.view_freight_operation_form',
                'res_model': 'freight.operation',
                'type': 'ir.actions.act_window',
                'res_id': freight.id,
                'context': self.env.context
            }


class InvoiceInherit(models.Model):
    _inherit = "account.move"

    direction = fields.Selection(([('import', 'Import'), ('export', 'Export'), ('crosstrade', 'Crosstrade')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    freight_select_payable =fields.Boolean(string="Payable")
    freight_move_group_ids=fields.One2many("freight.invoice.group",'move_id')
    freight_container_lines=fields.One2many("freight.invoice.containers",'move_id')

class freightInvoiceGroup(models.Model):
    _name="freight.invoice.group"
    _description="freight product from job is grouped by container size and charge type "
    charge_type_id=fields.Many2one("freight.charge.type")
    move_id=fields.Many2one("account.move")
    port_of_loading=fields.Many2one("freight.port","POL")
    port_of_delivery=fields.Many2one("freight.port","POD")
    container_size=fields.Many2one("freight.container.size",string="Cont.Size")
    container_type=fields.Many2one("freight.container.type",string="Cont.Type")
    qty=fields.Char("Qty")
    _sql_constraints = [
                (
                    "invoice_ports_chargeContainer_unique",
                    "unique(charge_type_id,port_of_delivery,port_of_loading, move_id, container_size)",
                    "container size and charge type must be unique per invoice",
                )
            ]
class freightInvoicecontainers(models.Model):
    _name="freight.invoice.containers"
    _description="freight containers and qty invoiced "
    move_id=fields.Many2one("account.move")
    container_size=fields.Many2one("freight.container.size",string="Cont.Size")
    container_type=fields.Many2one("freight.container.type",string="Cont.Type")
    qty=fields.Float("Qty",default=1)
    _sql_constraints = [
                (
                    "invoice_Container_unique",
                    "unique( move_id,container_type, container_size)",
                    "container size and  type must be unique per invoice",
                )
            ]

    @api.onchange("qty")
    def container_qty_changed(self):
        invoiceLines=self.env['account.move.line'].search([("move_id",'=',self.move_id._origin.id),("freight_container_size",'=',self.container_size.id),
                                                           ("freight_container_type",'=',self.container_type.id),("rate_basis",'=',3)])
        # for line in invoiceLines:
        #     line._write({"quantity": self.qty})
        #     line.update(line._get_price_total_and_subtotal())
        #     line.update(line._get_fields_onchange_subtotal())

class FreightChargeType(models.Model):
    _name ="freight.charge.type"
    name=fields.Char("Name")
    description=fields.Char("Details")



class FreightCharge(models.Model):
    _inherit = "product.template"
    charge_type=fields.Many2one("freight.charge.type","FreightCharge Type")

class FreightCharge(models.Model):
    _name ="freight.charge"
    name=fields.Char("Name")
    details=fields.Char("Details")
    charge_type=fields.Many2one("freight.charge.type","FreightCharge Type")



class FreightDestinationCharges(models.Model):
    _name ="freight.destination.charges"
    country = fields.Many2one('res.country', 'Applicable Country')
    state = fields.Many2one('res.country.state', 'Applicable State', domain="[('country_id', '=', country)]")
    air = fields.Boolean(string='Applicable Air')
    ocean = fields.Boolean(string='Applicable Ocean')
    land = fields.Boolean(string='Applicable Land')

    #todo extend this domain for ,('air', '=', air),"  "('ocean', '=', ocean),('land', '=', land)
    port_id=fields.Many2one('freight.port',"Applicable Port", domain="[('country', '=', country)]")
    active = fields.Boolean(default=True, string='Active')

    charge_heading=fields.Many2one("freight.charge","Charge Heading")
    rate_basis=fields.Many2one("freight.rate.basis","Rate Basis")
    currency=fields.Many2one("res.currency")
    charge=fields.Monetary(string='Amount', currency_field='currency')
    container_lines=fields.One2many("freight.order.line.container.line","destination_charge_id","container_lines")



    @api.onchange('country','state','air','ocean','land')
    def get_domain_for_port(self):
        domain=[]
        if self.country:
            domain_string=('country','=',self.country.id)
            domain.append(domain_string)
        if self.state:
            domain_string=('state','=',self.state.id)
            domain.append(domain_string)
        if self.air:
            domain_string=('air','=',self.air)
            domain.append(domain_string)
        if self.ocean:
            domain_string=('ocean','=',self.ocean)
            domain.append(domain_string)
        if self.land:
            domain_string=('land','=',self.land)
            domain.append(domain_string)
        ports=self.env['freight.port'].search(domain)
        res={}
        res['domain']={'port_id':[('id','in',ports.ids)]}

        return res

class QuotationLineDetails(models.Model):
    _name ="freight.order.line.details"
    order_line_id=fields.Many2one("sale.order.line","Order Line")
    charge_heading=fields.Many2one("freight.charge","Charge Heading")
    rate_basis=fields.Many2one("freight.rate.basis","Rate Basis")
    currency=fields.Many2one("res.currency")
    amount=fields.Float("Freight",default=0.0)
    # container_20 = fields.Float('20GE',  default=0.0)
    # container_40 = fields.Float('40GE',  default=0.0)
    # container_40hc = fields.Float('40HC',  default=0.0)
    container_lines=fields.One2many("freight.order.line.container.line","order_line_id","container_lines")

class freightOrderLineContainerLine(models.Model):
    _name="freight.order.line.container.line"
    _rec_name='container_type'
    order_line_id=fields.Many2one("freight.order.line.details","Order Line")
    destination_charge_id=fields.Many2one("freight.destination.charges","Deestination Charge")
    container_type=fields.Many2one ("freight.container.type", "Container Type")
    container_freight=fields.Float("Freight",default=0.0)

class QuotationLineFrFieldInherit(models.Model):
    _inherit = "sale.order.line"

    selected=fields.Boolean("Select")
    freight_details=fields.One2many("freight.order.line.details",'order_line_id','freight_details')
    port_of_loading = fields.Many2one('freight.port', string="POL", store=True)
    port_of_delivery = fields.Many2one('freight.port', string="POD", store=True)
    freight_item_qty = fields.Integer("Vol. Qty", store=True)
    freight_container_type = fields.Many2one('freight.container.type',"container Type")
    rate_basis = fields.Many2one("freight.rate.basis", "Rate Basis")
    # freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #         ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', store=True)
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1), store=True)

    freight_20ge = fields.Float(string="20 GE", digits=(12,1),store=True) #compute="get_container_freight", inverse="set_container_freight")
    freight_40ge = fields.Float(string="40 GE", digits=(12,1), store=True)
    freight_40hc = fields.Float(string="40 HC", digits=(12,1), store=True)

    # def get_container_freight(self):
    #     for rec in self:





    freight_etd = fields.Date(string='ETD', store=True)
    rate_validity = fields.Date(string='Rate Validity', store=True)
    foreign_currency = fields.Many2one('res.currency', string='Curr.', store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate', compute='_compute_ex_currency')
    rate_as_currency = fields.Float(string='Unt Rate (Forex)', compute='_compute_currency', inverse='_inverse_price_unit')
    amount_as_currency = fields.Float(string='Amount (Forex)', compute='_compute_currency')
    job_line_id = fields.Many2one('freight.operation.line', string='Created Job')
    job_service_line_id = fields.Many2one('freight.service.line', string='Created Job')

    def open_to_form_view(self, context=None):

        if not context:
            context = {}

        # name = '<Name>'
        # res_model = '<model>'
        # view_name = '<view>'

        document_id = self.id
        # view = models.get_object_reference(cr, uid, name, view)
        # view_id = view and view[1] or False

        return {
            'name': "(name)",
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('freight_in_quotation.freight_order_line_form').id,
            'res_model': "sale.order.line",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': self.id,
        }
    @api.onchange('rate_as_currency')
    def _compute_ex_currency(self):
        for rec in self:
            rec.ex_currency_rate = 1 / rec.foreign_currency.rate

    def action_view_details(self):
        action = self.env["ir.actions.actions"]._for_xml_id("freight_in_quotation.freight_quotation_line_details_action")
        action['domain'] = [('order_line_id', 'in', self.ids)]
        return action



    @api.onchange('rate_as_currency')
    def _inverse_price_unit(self):
        for rec in self:
            # rec.rate_as_currency = rec.price_unit * rec.foreign_currency.rate
            rec.price_unit = rec.rate_as_currency /rec.foreign_currency.rate
            rec.amount_as_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    @api.onchange('foreign_currency', 'price_unit', 'product_uom_qty')
    def _compute_currency(self):
        for rec in self:
            rec.rate_as_currency = rec.price_unit * rec.foreign_currency.rate
            rec.amount_as_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    def create_freight_job(self):
        for rec in self:
            if rec.job_line_id.id and rec.job_service_line_id.id==False:
                values = {
                    # 'name': rec.id,
                    'direction': rec.order_id.direction,
                    'transport': rec.order_id.transport,
                    'ocean_shipment_type': rec.order_id.ocean_shipment_type,
                    'inland_shipment_type': rec.order_id.inland_shipment_type,
                    'shipper_id': rec.order_id.partner_id.id,
                    'datetime': rec.order_id.date_order,
                    'operation': 'direct',
                    # 'quotation_id': rec.order_id.id,
                }

                freight = self.env['freight.operation'].create(values)

                for line in self:
                    line_vals = {
                        'operation_id': freight.id,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.product_uom_qty,
                        "product_uom": line.product_uom.id,
                        "port_of_loading": line.port_of_loading.id,
                        "port_of_delivery": line.port_of_delivery.id,
                        # "freight_item_qty": line.freight_item_qty,
                        "freight_container_type": line.freight_container_type,
                        "freight_teus20ft": line.freight_teus20ft,
                        "freight_ffe40ft": line.freight_ffe40ft,
                        "freight_etd": line.freight_etd,
                        "rate_validity": line.rate_validity,
                        "foreign_currency": line.foreign_currency.id,
                        "ex_currency_rate": line.ex_currency_rate,
                        "rate_as_currency": line.rate_as_currency,
                        "amount_as_currency": line.amount_as_currency,
                        "price_unit": line.price_unit,
                        "price_subtotal": line.price_subtotal,
                    }
                    freight_line = self.env['freight.operation.line'].create(line_vals)
                    self.job_line_id=freight_line.id

                    service_line = self.env['freight.service.line'].create(line_vals)
                    self.service_line_id=service_line.id
            else:
                freight = self.job_line_id.operation_id
            return {
                # 'name': _('Job Name'),
                'view_type': 'form',
                'view_mode': 'form',
                # 'view_id': 'freight.view_freight_operation_form',
                'res_model': 'freight.operation',
                'type': 'ir.actions.act_window',
                'res_id': freight.id,
                'context': self.env.context
            }


    @api.onchange('product_uom_qty', 'freight_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.freight_teus20ft = (rec.product_uom_qty * int(rec.freight_container_type)) / 2000
            rec.freight_ffe40ft = (rec.product_uom_qty * int(rec.freight_container_type)) / 4000



    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'port_of_loading': self.port_of_loading,
            'port_of_delivery': self.port_of_delivery,

            # 'freight_item_qty': self.freight_item_qty,
            'freight_container_type': self.freight_container_type,
            'freight_container_size': self.container_size,
            'rate_basis': self.rate_basis,
            'freight_teus20ft': self.freight_teus20ft,
            'freight_ffe40ft': self.freight_ffe40ft,
            'freight_etd': self.freight_etd,
            'rate_validity': self.rate_validity,
            'foreign_currency': self.foreign_currency,
            'ex_currency_rate': self.ex_currency_rate,
            'rate_as_currency': self.rate_as_currency,
            'amount_as_currency': self.amount_as_currency,
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res


class FreightquotefieldtoAccount(models.Model):
    _inherit = 'account.move.line'

    port_of_loading = fields.Many2one('freight.port', string="POL")
    port_of_delivery = fields.Many2one('freight.port', string="POD")
    invoice_group_id=fields.Many2one("freight.invoice.group")
    # freight_item_qty = fields.Integer("Vol. Qty", store=True)
    rate_basis = fields.Many2one("freight.rate.basis")
    freight_container_size = fields.Many2one("freight.container.size",string="cont.Size")
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12, 1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12, 1), store=True)
    rate_validity = fields.Date(string='Rate Validity')
    freight_etd = fields.Date(string='ETD')

    foreign_currency = fields.Many2one('res.currency', string='Curr.', default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate', compute='_compute_ex_currency')
    rate_as_currency = fields.Float(string='Unt Rate (Forex)', compute='_compute_currency')
    amount_as_currency = fields.Float(string='Amount (Forex)', compute='_compute_currency')

    @api.onchange('rate_as_currency')
    def _compute_ex_currency(self):
        for rec in self:
            rec.ex_currency_rate = 1 / rec.foreign_currency.rate

    @api.onchange('foreign_currency', 'price_unit', 'quantity')
    def _compute_currency(self):
        for rec in self:
            rec.rate_as_currency = rec.price_unit * rec.foreign_currency.rate
            rec.amount_as_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.quantity


    @api.onchange('quantity', 'freight_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.freight_teus20ft = (rec.quantity * int(rec.freight_container_type)) / 2000
            rec.freight_ffe40ft = (rec.quantity * int(rec.freight_container_type)) / 4000


class QuotationServiceLine(models.Model):
    _name = 'quotation.service.line'
    _description='Service order Line'

    selected=fields.Boolean("Select")
    sale_order_id = fields.Many2one('sale.order', 'Sale Order Id')
    operation_id = fields.Many2one('freight.operation', string='Operation ID')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one('uom.uom', 'Unit')
    price_unit = fields.Float('Unt Rate (AED)')
    price_subtotal = fields.Float('Amount (AED)')
    product_uom_qty = fields.Float('Qty', default="1")

    port_of_loading = fields.Many2one('freight.port', string="POL", store=True)
    port_of_delivery = fields.Many2one('freight.port', string="POD", store=True)

    freight_20ge = fields.Float(string="20 GE", digits=(12,1), store=True)
    freight_40ge = fields.Float(string="40 GE", digits=(12,1), store=True)
    freight_40hc = fields.Float(string="40 HC", digits=(12,1), store=True)

    freight_item_qty = fields.Integer("Vol. Qty", store=True)
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    # freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #         ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', store=True)
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1), store=True)

    freight_etd = fields.Date(string='ETD', store=True)
    rate_validity = fields.Date(string='Rate Validity', store=True)

    foreign_currency = fields.Many2one('res.currency', string='Curr.', store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate', compute='_compute_ex_currency')
    rate_as_currency = fields.Float(string='Unt Rate (Forex)', compute='_compute_currency', inverse='_inverse_price_unit')
    amount_as_currency = fields.Float(string='Amount (Forex)', compute='_compute_currency')
    job_service_line_id = fields.Many2one('freight.service.line', string='Created Job')

    @api.onchange('rate_as_currency')
    def _compute_ex_currency(self):
        for rec in self:
            rec.ex_currency_rate = 1 / rec.foreign_currency.rate

    @api.onchange('rate_as_currency')
    def _inverse_price_unit(self):
        for rec in self:
            # rec.rate_as_currency = rec.price_unit * rec.foreign_currency.rate
            rec.price_unit = rec.rate_as_currency /rec.foreign_currency.rate
            rec.amount_as_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    @api.onchange('foreign_currency', 'price_unit', 'product_uom_qty')
    def _compute_currency(self):
        for rec in self:
            rec.rate_as_currency = rec.price_unit * rec.foreign_currency.rate
            rec.amount_as_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.product_uom_qty


    @api.onchange('product_id','product_uom','product_uom_qty','price_unit')
    def calculate_prices(self):
        for rec in self:
            rec.price_subtotal=rec.price_unit*rec.product_uom_qty

    @api.onchange('product_id')
    def get_product_price(self):
        for rec in self:
            rec.price_unit=rec.product_id.with_context(pricelist=self.sale_order_id.partner_id.property_product_pricelist.id).price
            rec.price_subtotal=rec.price_unit*rec.product_uom_qty


