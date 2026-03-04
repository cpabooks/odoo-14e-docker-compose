from decimal import Decimal

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class JobOrder(models.Model):
    _name = 'quotation.job.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # readonly_field=fields.Boolean(compute="_set_readonly")

    system_admin = fields.Boolean(compute="_get_system_admin")

    sale_person=fields.Many2one('res.users',string="Sales Person")
    remark=fields.Char(string="Remarks")
    breaker = fields.Char(string="Breaker")
    elr = fields.Char(string="ELR: CBCT & CT")
    enclosure = fields.Char(string="Enclosure")
    brand = fields.Char(string="Brand")
    note=fields.Text(string="Note")
    print_manual_job = fields.Boolean(string="Print Manual Job Order?")

    manual_job = fields.Char(string="Manual Job Order")

    @api.depends('state')
    def _get_system_admin(self):
        for rec in self:
            get_admin_power_group = self.env['res.groups'].sudo().search([('name', '=ilike', 'Admin Power')])
            if get_admin_power_group:
                if self.env.user.has_group('base.group_system') or self.env.user.id in get_admin_power_group.users.ids:
                    rec.system_admin = True
                else:
                    rec.system_admin = False
            else:
                if self.env.user.has_group('base.group_system'):
                    rec.system_admin = True
                else:
                    rec.system_admin = False


    name=fields.Char(string="Number", default="/")
    lpo_number=fields.Char(string="LPO")
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    project_id=fields.Many2one('project.project' , string="Project/Job")
    enquiry_number=fields.Char(string="Enquiry Number")
    attention=fields.Char(string="Attention")
    subject=fields.Char(string="Subject")
    delivery=fields.Char(string="Delivery")
    make=fields.Char(string="Make")
    bank_detail_enable=fields.Boolean(string="Bank Detail Enable")
    validity_date = fields.Date(string='Expiration')
    job_order_date= fields.Date(string='Job Order Date')
    quotation_no=fields.Many2one("sale.order",domain="[('job_quotation','=',True)]")
    order_line=fields.One2many("quotation.job.order.line","job_order_id",string="Job Order Line")
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirm'),
        ('cancelled', 'Cancel'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    total_quantity=fields.Monetary(string="Total Quantity",compute="_get_total_quantity")
    total_remaining_quantity=fields.Monetary(string="Total Remaining Quantity",compute="_get_total_quantity")
    total_delivered_quantity = fields.Monetary(string="Total Delivered Quantity", compute="_get_total_quantity")
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    warehouse_id=fields.Many2one('stock.warehouse' , string="Warehouse")
    delivery_count=fields.Integer(compute="_get_delivery")
    show_delivery_button=fields.Boolean(compute="calculated_show_delivery_button")
    job_description=fields.Text(string="Job Description")


    @api.depends("state")
    def calculated_show_delivery_button(self):
        for rec in self:
            self.show_delivery_button = False
            for line in rec.order_line:
                if line.product_uom_qty - line.delivered_qty > 0:
                    self.show_delivery_button = True
                    break;

    # def _set_readonly(self):
    #     sum_of_job_order_delivered_line=
    def get_ref(self):
        for rec in self:
            get_customer_ref=self.env['sale.order'].search([('name','=',rec.quotation_no.id)]).client_order_ref
            return get_customer_ref

    def get_signature(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'signature.setup')])
        if get_model:
            get_signature_data = self.env['signature.setup'].search(
                [('model', '=', 'quotation.job.order'), ('company_id', '=', self.env.company.id)])
            return get_signature_data
        else:
            return []

    def _get_sequence(self,get_sequence_object,get_sequence,vals_list,get_highest_purchase,job_order_name):
        if '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern=='month_year':
            if job_order_name != '':
                split_job_order_name = job_order_name.split('/')
                split_seq = get_sequence.split('/')
                split_job_order_name_last_value = split_job_order_name[-1]
                split_seq[-1] = split_job_order_name_last_value
                if get_highest_purchase and get_highest_purchase.name!='/':
                    split_highest_inv=get_highest_purchase.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])-1
                    get_sequence_object.number_next_actual=get_sequence_object.number_next_actual-1
            else:
                split_seq = get_sequence.split('/')
                # split_highest_inv = get_highest_purchase.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'],
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month=datetime.now().month
                    str_month=str(datetime.now().month)
                    if month<10:
                        str_month=str(0)+str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[1]
                    get_sequence = "/".join(split_seq)
            if 'job_order_date' not in vals_list.keys() and not isinstance(self.job_order_date,
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.job_order_date).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.job_order_date).split('-')[1]
                    get_sequence = "/".join(split_seq)
            return get_sequence

        elif '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern=='month_year_monthly':
            if get_sequence != '':
                split_inv_name = get_sequence.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_purchase and get_highest_purchase.name!='/':
                    split_highest_inv=get_highest_purchase.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                # split_highest_inv = get_highest_inv.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'],
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month=datetime.now().month
                    str_month=str(datetime.now().month)
                    if month<10:
                        str_month=str(0)+str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[1]
                    get_sequence = "/".join(split_seq)

                    # region Month wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"
                    get_highest_sequence = self.env['quotation.job.order'].search(
                        [('name', 'like', without_last_index_sequence), ('id', '!=', self.id)],
                        order="id desc",
                        limit=1)
                    sequence_padding = get_sequence_object.padding
                    get_highest_sequence_no = 0
                    if get_highest_sequence:
                        highest_seq = get_highest_sequence.name.split('/')
                        get_highest_sequence_no = int(highest_seq[-1])
                    if len(str(get_highest_sequence_no)) > sequence_padding:
                        number = get_highest_sequence_no + 1
                        string_convert = str(number)
                        orginal_sequence[-1] = string_convert
                    else:
                        common='1'
                        divide_by=int(common.ljust(sequence_padding+1,'0'))
                        number = (get_highest_sequence_no + 1) / divide_by
                        dec_string = str(round(Decimal(number), sequence_padding))
                        string_convert = dec_string.split('.')[1]
                        orginal_sequence[-1] = string_convert

                    get_sequence = "/".join(orginal_sequence)
                    # endregion
            if 'job_order_date' not in vals_list.keys() and not isinstance(self.job_order_date,
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.job_order_date).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.job_order_date).split('-')[1]
                    get_sequence = "/".join(split_seq)
                    #region Month wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"
                    get_highest_sequence = self.env['quotation.job.order'].search(
                        [('name', 'like', without_last_index_sequence), ('id', '!=', self.id)],
                        order="id desc",
                        limit=1)
                    sequence_padding = get_sequence_object.padding
                    get_highest_sequence_no = 0
                    if get_highest_sequence:
                        highest_seq = get_highest_sequence.name.split('/')
                        get_highest_sequence_no = int(highest_seq[-1])
                    if len(str(get_highest_sequence_no)) > sequence_padding:
                        number = get_highest_sequence_no + 1
                        string_convert = str(number)
                        orginal_sequence[-1] = string_convert
                    else:
                        common='1'
                        divide_by=int(common.ljust(sequence_padding+1,'0'))
                        number = (get_highest_sequence_no + 1) / divide_by
                        dec_string = str(round(Decimal(number), sequence_padding))
                        string_convert = dec_string.split('.')[1]
                        orginal_sequence[-1] = string_convert

                    get_sequence = "/".join(orginal_sequence)
                    #endregion
            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern=='year' :
            if job_order_name != '':
                split_inv_name = job_order_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_purchase and get_highest_purchase.name!='/':
                    split_highest_inv=get_highest_purchase.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
            if 'job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'],
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)

            if 'job_order_date' not in vals_list.keys() and not isinstance(self.job_order_date,
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.job_order_date).split('-')[0]
                    get_sequence = "/".join(split_seq)


            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern=='year_yearly':
            if job_order_name != '':
                split_inv_name = job_order_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_purchase and get_highest_purchase.name != '/':
                    split_highest_inv = get_highest_purchase.name.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            if 'job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'],
                                                                     bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)

                    # region year wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"
                    get_highest_sequence = self.env['quotation.job.order'].search(
                        [('name', 'like', without_last_index_sequence), ('id', '!=', self.id)],
                        order="id desc",
                        limit=1)
                    sequence_padding = get_sequence_object.padding
                    get_highest_sequence_no = 0
                    if get_highest_sequence:
                        highest_seq = get_highest_sequence.name.split('/')
                        get_highest_sequence_no = int(highest_seq[-1])
                    if len(str(get_highest_sequence_no))>sequence_padding:
                        number=get_highest_sequence_no+1
                        string_convert=str(number)
                        orginal_sequence[-1] = string_convert
                    else:
                        common='1'
                        divide_by=int(common.ljust(sequence_padding+1,'0'))
                        number = (get_highest_sequence_no + 1) / divide_by
                        dec_string = str(round(Decimal(number), sequence_padding))
                        string_convert = dec_string.split('.')[1]
                        orginal_sequence[-1] = string_convert

                    get_sequence = "/".join(orginal_sequence)
                    # endregion

            if 'job_order_date' not in vals_list.keys() and not isinstance(self.job_order_date,
                                                                         bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.job_order_date).split('-')[0]
                    get_sequence = "/".join(split_seq)

                    # region year wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"
                    get_highest_sequence = self.env['quotation.job.order'].search(
                        [('name', 'like', without_last_index_sequence), ('id', '!=', self.id)],
                        order="id desc",
                        limit=1)
                    sequence_padding = get_sequence_object.padding
                    highest_seq = get_highest_sequence.name.split('/')
                    get_highest_sequence_no = int(highest_seq[-1])
                    if len(str(get_highest_sequence_no)) > sequence_padding:
                        number = get_highest_sequence_no + 1
                        string_convert = str(number)
                        orginal_sequence[-1] = string_convert
                    else:
                        common='1'
                        divide_by=int(common.ljust(sequence_padding+1,'0'))
                        number = (get_highest_sequence_no + 1) / divide_by
                        dec_string = str(round(Decimal(number), sequence_padding))
                        string_convert = dec_string.split('.')[1]
                        orginal_sequence[-1] = string_convert

                    get_sequence = "/".join(orginal_sequence)
                    # endregion

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(month)s/' in get_sequence_object.prefix:
            if job_order_name != '':
                split_inv_name = job_order_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_purchase and get_highest_purchase.name != '/':
                    split_highest_inv = get_highest_purchase.name.split('/')
                    get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            else:
                split_seq = get_sequence.split('/')
            if 'job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'],
                                                                     bool):
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['job_order_date']).split('-')[1]
                    get_sequence = "/".join(split_seq)
            if 'job_order_date' not in vals_list.keys() and not isinstance(self.job_order_date,
                                                                         bool):

                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.job_order_date).split('-')[1]
                    get_sequence = "/".join(split_seq)
            return get_sequence


        else:
            if job_order_name != '':
                split_inv_name = job_order_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                get_sequence = "/".join(split_seq)
                if get_highest_purchase and get_highest_purchase.name != '/':
                    split_highest_inv = get_highest_purchase.name.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual =get_sequence_object.number_next_actual-1
            else:
                split_seq = get_sequence.split('/')
                get_sequence = "/".join(split_seq)
            return get_sequence

    @api.model
    def create(self, vals_list):
        print(vals_list)
        res = super(JobOrder, self).create(vals_list)
        # get_sequence = self.env['ir.sequence'].next_by_sequence_for('job_order')
        # if not get_sequence:
        #     raise ValidationError(_("Sequence is not set for Job order"))
        # res.name = get_sequence or _('/')
        # return res
        company_id = self.env.company.id
        get_sequence_object = self.env['ir.sequence'].sudo().search(
            [('sequence_for', '=', 'job_order'), ('company_id', 'in', [company_id, False])],
            limit=1, )
        if res.name != '/' or res.name.upper() != 'DRAFT' or res.name.upper() != 'NEW':
            job_order_name = ''
        if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
            job_order_name = ''
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('job_order')
        if get_sequence:
            get_highest_po = self.env['quotation.job.order'].sudo().search([('id', '!=', self.id)], limit=1, order='id desc')
            get_sequence = res._get_sequence(get_sequence_object, get_sequence, vals_list, get_highest_po,
                                             job_order_name)
        if not get_sequence:
            raise ValidationError(_("Sequence is not set for Job order"))
        res.name = get_sequence or _('/')
        return res
    
    def write(self,vals_list):
        rec=super(JobOrder, self).write(vals_list)
        company_id = self.env.company.id
        for res in self:
            job_order_name = ''
            if ('job_order_date' in vals_list.keys() and not isinstance(vals_list['job_order_date'], bool)) or(res.name=='/' and not isinstance(res.job_order_date, bool)):
                    get_sequence_object = self.env['ir.sequence'].sudo().search(
                        [('sequence_for', '=', 'job_order'), ('company_id', 'in', [company_id, False])],
                        limit=1, )
                    if res.name!='/' or res.name.upper()!='DRAFT' or res.name.upper()!='NEW':
                        job_order_name=res.name
                    if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
                        job_order_name = ''
                    if job_order_name!='':
                        get_sequence = self.env['ir.sequence'].next_by_sequence_for('job_order')
                        if get_sequence:
                            get_highest_purchase = self.env['quotation.job.order'].sudo().search([('id','!=',self.id)],
                                                                                     limit=1,
                                                                                     order='id desc')
                            get_sequence = res._get_sequence(get_sequence_object, get_sequence, vals_list,
                                                             get_highest_purchase,job_order_name)



                        if not get_sequence:
                            raise ValidationError(_("Sequence is not set for Job order"))
                        res.name=get_sequence or _('/')




        return rec

    @api.depends('state')
    def _get_delivery(self):
        for rec in self:
            delivery_count=self.env['stock.picking'].sudo().search_count([('job_order_id','=',self.id)])
            rec.delivery_count=delivery_count


    def show_job_order_delivery(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        if self.delivery_count > 1:
            action['domain'] = [('job_order_id', '=', self.id)]
        else:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            get_delivery = self.env['stock.picking'].sudo().search([('job_order_id','=',self.id)])
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = get_delivery.id
        action['context'] = dict(self._context, default_job_order_id=self.id, create=False)
        return action

    @api.depends('state')
    def _get_job_orders(self):
        get_delivery=self.env['stock.picking'].sudo().search_count([('job_order_id','=',self.id),('is_job_order_delivery','=',True)])
        self.delivery_count=get_delivery

    @api.depends('state')
    def _get_total_quantity(self):
        for rec in self:
            total=0
            total_remaining=0
            total_delivered=0
            for line in rec.order_line:
                total+=line.product_uom_qty
                total_remaining+=line.remaining_qty
                total_delivered+=line.delivered_qty
            rec.total_quantity=total
            rec.total_remaining_quantity=total-total_delivered
            rec.total_delivered_quantity=total_delivered

    def action_confirmed(self):
        for rec in self:
            flag=0
            if rec.quotation_no:
                quotation_line=rec.quotation_no.order_line
                for line in rec.order_line:
                    for qt_line in quotation_line:
                        if qt_line.id==line.quotation_line_id.id:
                            if line.product_uom_qty==0:
                                raise ValidationError(_("Line With Zero Quantity is not Allowed Please Remove it"))
                            if (qt_line.product_uom_qty-qt_line.job_order_qty) >= line.product_uom_qty:
                                if line.quotation_line_id.id==qt_line.id:
                                    flag = 1
                                    qt_line.job_order_qty+=line.product_uom_qty
                                    qt_line.remaining_qty=qt_line.product_uom_qty-qt_line.job_order_qty
                            else:
                                raise ValidationError(_("You can not confirm more job order quantiy then quotation line quantity for:\n"+str(line.line_no)+". "+line.product_id.name))
            if flag==1:
                rec.state='confirmed'

    def unlink(self):
        for rec in self:
            total_delivered=sum(rec.order_line.mapped('delivered_qty'))
            if total_delivered>0:
                raise ValidationError(_("You can not delete a job order which is already delivered"))
            else:
                if rec.state=='confirmed':
                    quotation_line = rec.quotation_no.order_line
                    for line in rec.order_line:
                        for qt_line in quotation_line:
                            if line.quotation_line_id.id == qt_line.id:
                                qt_line.job_order_qty -= line.product_uom_qty
                                qt_line.remaining_qty = qt_line.product_uom_qty - qt_line.job_order_qty

    def action_create_delivery(self):
        form_view_id = self.env.ref("stock.view_picking_form").id
        delivery_line=[]
        for rec in self:

            for line in rec.order_line:
                vals=(0,0,{
                    'product_id':line.product_id.id,
                    'product_description':line.name,
                    'description_picking':line.name,
                    'product_uom_qty':line.product_uom_qty-line.delivered_qty,
                    'product_uom':line.product_uom.id,
                    'name':line.product_id.name,
                    'job_line_id':line.id,
                    'quotation_line_id':line.quotation_line_id.id,
                    # 'state':'assigned',
                    'move_line_ids':[(0,0,{
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        # 'product_uom_qty': line.product_uom_qty - line.delivered_qty,
                        'location_id': rec.warehouse_id.lot_stock_id.id,
                        'location_dest_id': 5,
                        # 'state': 'assigned',
                        'product_description': line.name
                    })]
                })
                delivery_line.append(vals)
            # delivery_picking={
            #     'default_partner_id':rec.partner_id.id,
            #     'default_picking_type_id':self.env['stock.picking.type'].sudo().search([('code','=','outgoing'),('warehouse_id','=',rec.warehouse_id.id)],limit=1).id,
            #     'default_location_id':rec.warehouse_id.lot_stock_id.id,
            #     'default_origin':rec.name,
            #     'default_move_ids_without_package':delivery_line,
            #     'default_project_id': rec.project_id.id,
            #     'default_job_order_id':rec.id,
            #     'default_is_job_order_delivery':True,
            #     'lpo_number':rec.lpo_number
            # }
            delivery_picking = {
                'partner_id': rec.partner_id.id,
                'picking_type_id': self.env['stock.picking.type'].sudo().search(
                    [('code', '=', 'outgoing'), ('warehouse_id', '=', rec.warehouse_id.id)], limit=1).id,
                'location_id': rec.warehouse_id.lot_stock_id.id,
                'location_dest_id':5,
                'origin': rec.name,
                'move_ids_without_package': delivery_line,
                'project_id': rec.project_id.id,
                'job_order_id': rec.id,
                'is_job_order_delivery': True,
                'lpo_number': rec.lpo_number,
                # 'state':'assigned'
            }
        res= self.env['stock.picking'].sudo().create(delivery_picking)
        for picking in res:
            for stock_move in picking.move_ids_without_package:
                for stock_move_line in stock_move.move_line_ids:
                    stock_move_line.picking_id=picking.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Order Delivery',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'views': [(form_view_id, 'form')],
            'target': 'current',
            # 'context':delivery_picking
            'res_id':res.id

        }




    def action_reset_to_draft(self):
        for rec in self:
            if rec.quotation_no and rec.state=='confirmed':
                quotation_line=rec.quotation_no.order_line
                for line in rec.order_line:
                    for qt_line in quotation_line:
                        if line.quotation_line_id.id==qt_line.id:
                            qt_line.job_order_qty-=line.product_uom_qty
                            qt_line.remaining_qty=qt_line.product_uom_qty-qt_line.job_order_qty
            rec.state='draft'

    def action_cancel(self):
        for rec in self:
            total_delivered = sum(rec.order_line.mapped('delivered_qty'))
            if total_delivered > 0:
                raise ValidationError(_("You can not cancel a job order which is already delivered"))
            else:
                if rec.state=='confirmed':
                    quotation_line = rec.quotation_no.order_line
                    for line in rec.order_line:
                        for qt_line in quotation_line:
                            if line.quotation_line_id.id == qt_line.id:
                                qt_line.job_order_qty -= line.product_uom_qty
                                qt_line.remaining_qty = qt_line.product_uom_qty - qt_line.job_order_qty
            rec.state='cancelled'


class JobOrderLine(models.Model):
    _name = 'quotation.job.order.line'

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.job_order_id.order_line:
                if line_rec.display_type not in ('line_section', 'line_note'):
                    line_rec.line_no = line_num
                    line_num += 1

    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    job_order_id=fields.Many2one("quotation.job.order")
    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)
    product_id=fields.Many2one('product.product',string="Product")
    name=fields.Text(string="Description")
    product_uom = fields.Many2one('uom.uom', string="UoM")
    product_uom_qty=fields.Float(string="Quantity")
    quotation_line_id=fields.Many2one('sale.order.line', string="Quotation Line No")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    remaining_qty = fields.Float(string="Remaining qty")
    delivered_qty = fields.Float(string="Delivered qty")



