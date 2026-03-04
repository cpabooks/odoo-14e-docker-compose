from odoo import models, fields, api, _

class PaymentCertificate(models.Model):
    _name = "payment.certificate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name=fields.Char(default=lambda self: _('New') ,copy=False, readonly=True)
    project_no=fields.Many2one("project.project",string="Project No.")
    Project_name=fields.Char(related="project_no.name",string="Project Name")
    contractor_name=fields.Many2one("res.partner",related="project_no.partner_id",string="Contract/Customer Name")
    vendor_name=fields.Many2one("res.partner",string="Contractor/Vendor Name")
    # contract=fields.Char(string="Contract")
    # contract_type=fields.Many2one('project.default.task',string="Contract Type",domain=lambda self:[('id','in',self.env['project.default.task'].search([('parent_id','=',None)]).ids)])

    date=fields.Datetime(string="Date")
    # pc_no=fields.Char(string="PC No.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    payment_certificate_line = fields.One2many('payment.certificate.line', 'certificate_id', string='Payment Certificate Lines')
    sub_total_amount = fields.Monetary(string='SUB-Total', store=True, readonly=True, compute='_amount_all', tracking=True)
    retention_amount = fields.Monetary(string='Retention Amount(10%)', store=True, readonly=True, compute='set_retention_amount')
    previous_payment_amount = fields.Monetary(string='Previous Payments',compute="_previous_amount", store=True, readonly=True)
    other_deduction_amount = fields.Float(string='Other Deduction')
    net_payment_due_amount = fields.Monetary(string='Net Payment Due (DHS)', store=True, readonly=True, compute='_amount_all')
    company_id=fields.Many2one("res.company",default=lambda self:self.env.company.id)
    contract_value =fields.Char(string="Contract Value")
    retention_percentage=fields.Float( digits=(16, 1))

    @api.depends("retention_percentage","sub_total_amount")
    def set_retention_amount(self):
        for rec in self:
            rec.retention_amount=rec.sub_total_amount*(rec.retention_percentage/100)
            rec.net_payment_due_amount = rec.sub_total_amount - rec.retention_amount - rec.previous_payment_amount - rec.other_deduction_amount

    @api.depends("vendor_name")
    def _previous_amount(self):
        get_prev_payment = self.env["payment.certificate"]
        for rec in self:
            if rec.vendor_name:
                if rec.ids:
                    get_prev_payment = self.env["payment.certificate"].search([('vendor_name','=',self.vendor_name.id),('id','!=',rec.ids[0])],order="id desc",limit=1)
                else:
                    get_prev_payment = self.env["payment.certificate"].search(
                        [('vendor_name', '=', self.vendor_name.id)], order="id desc", limit=1)
            if get_prev_payment:
                rec.update({
                    'previous_payment_amount':get_prev_payment.net_payment_due_amount
                })
            else:
                rec.update({
                    'previous_payment_amount': 0
                })

    @api.depends('payment_certificate_line.amount_work_done','other_deduction_amount')
    def _amount_all(self):
        for rec in self:
            sub_total=0
            for done_work in rec.payment_certificate_line:
                sub_total+=done_work.amount_work_done
            rec.sub_total_amount=sub_total
            # rec.retention_amount=sub_total*.1
            rec.net_payment_due_amount=rec.sub_total_amount-rec.retention_amount-rec.previous_payment_amount-rec.other_deduction_amount
    # @api.depends("other_deduction_amount")
    # def _calculate_net_total(self):
    #     self.net_payment_due_amount-=self.other_deduction_amount

    # @api.onchange('project_no','contract_type')
    @api.onchange('project_no')
    def set_line_previous_qty(self):
        for rec in self:
            if rec.payment_certificate_line:
                for line in rec.payment_certificate_line:
                    line.previous_qty=0
                    get_previous_pc = self.env["payment.certificate.line"].search(
                        [('product_id', '=', line.product_id.id)],
                        order="certificate_id desc")

                    for previous in get_previous_pc:
                        # if previous.certificate_id.project_no == line.certificate_id.project_no and previous.certificate_id.contract_type == line.certificate_id.contract_type and previous.certificate_id.contractor_name == line.certificate_id.contractor_name:
                        if previous.certificate_id.project_no == line.certificate_id.project_no  and previous.certificate_id.contractor_name == line.certificate_id.contractor_name:
                            line.previous_qty = previous.total_qty
                            break;

    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.certificate') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.certificate')
        result = super(PaymentCertificate, self).create(vals)
        return result


class PaymentCertificateLine(models.Model):
    _name = "payment.certificate.line"

    certificate_id=fields.Many2one("payment.certificate" , string='Certificate Reference', index=True, required=True, ondelete='cascade')
    product_id=fields.Many2one('product.product', string="Description")
    unit=fields.Many2one('uom.uom',string="Unit")
    rate=fields.Float(string="Rate (DHS)")
    previous_qty=fields.Float(string="Previous Qty")
    previous_amt = fields.Float(string="Previous Amt",readonly=True,store=True)
    present_qty=fields.Float(string="Present Qty")
    present_amt = fields.Float(string="Present Amt",readonly=True,store=True)
    total_qty=fields.Float(string="Total Qty",compute="total_calculation" , store=True)
    total_amt = fields.Float(string="Total Amt", compute="total_calculation", store=True)
    amount_work_done=fields.Float(string="Amount of Work Done (DHS)",compute="total_calculation" , store=True)
    remarks=fields.Char(string="Status")


    @api.onchange("product_id")
    def onchange_product_id(self):
        for rec in self:
            rec.unit=rec.product_id.uom_id
            rec.rate=rec.product_id.lst_price

            # get_previous_pc = self.env["payment.certificate.line"].search([('product_id','=',rec.product_id.id)],order="id desc",limit=1)
            get_previous_pc = self.env["payment.certificate.line"].search([('product_id', '=', rec.product_id.id)],
                                                                          order="certificate_id desc")

            for previous in  get_previous_pc:
                # if previous.certificate_id.project_no==rec.certificate_id.project_no and previous.certificate_id.contract_type==rec.certificate_id.contract_type and previous.certificate_id.contractor_name==rec.certificate_id.contractor_name:
                if previous.certificate_id.project_no==rec.certificate_id.project_no and previous.certificate_id.contractor_name==rec.certificate_id.contractor_name:
                    rec.previous_qty = previous.total_qty
                    break;
            # if get_previous_pc:
            #     rec.previous_qty=get_previous_pc.total_qty

    @api.depends("previous_qty","present_qty","rate")
    def total_calculation(self):
        for rec in self:
            rec.present_amt=rec.rate*rec.present_qty
            rec.total_qty=rec.previous_qty+rec.present_qty
            rec.total_amt=rec.total_qty*rec.rate
            rec.amount_work_done=rec.total_qty*rec.rate
            rec.previous_amt=rec.rate*rec.previous_qty