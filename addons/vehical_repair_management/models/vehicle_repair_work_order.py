from odoo import api, models, fields, _
import base64
from odoo.exceptions import ValidationError, UserError


class VehicleRepairWorkOrder(models.Model):
    _name = 'vehicle.repair.work.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Vehicle Service Registration"
    _order = "id desc"




    name = fields.Char(string='Name', default="New", copy=False)
    customer_id = fields.Many2one('res.partner', 'Client', related='plate_no.customer_id', ondelete="restrict")
    date = fields.Datetime(string='Receiving Date', default=fields.Datetime.now)
    delivery_date = fields.Datetime(string='Delivery Date')
    phone = fields.Char(string='Phone', related="customer_id.phone", readonly=False)
    email = fields.Char(string="Email", related="customer_id.email", readonly=False)
    manager_ids = fields.Many2many('hr.employee', 'manager_repair_rel', 'manager_id', 'repair_id', string='Team Leader')
    repair_team_ids = fields.Many2many("vehicle.repair.team", string="Service Team")
    team_member_ids = fields.Many2many("hr.employee")
    # plate_no = fields.Char(string='Plate Number')
    plate_no = fields.Many2one('vehicle.detail.by.plate', 'Plate Number')
    plate_exist = fields.Boolean()
    before_service_image_ids = fields.One2many('vehicle.service.image', 'registration_id2',
                                               string='Before Service Image')
    after_service_image_ids = fields.One2many('vehicle.service.image', 'registration_id', string='After Service Image')
    used_part_ids = fields.One2many('vehicle.part.used.info', 'repair_work_order_id', ondelete="cascade")
    state = fields.Selection(
        [('draft', 'Draft'), ('cancel', 'Canceled'), ('confirm', 'Confirmed'), ('under_process', 'Under Process'),
         ('done', 'Done')], default='draft', copy=False, track_visibility='onchange')
    work_sheet_ids = fields.One2many('work.sheet', 'repair_work_order_id', string='Work Sheet', ondelete="cascade")
    accomplished_date = fields.Datetime(string='Accomplished Date')
    vehicle_type_id = fields.Many2one("vehicle.vehicle.type", related='plate_no.vehicle_type_id', ondelete="restrict")
    brand_id = fields.Many2one("vehicle.brand", related='plate_no.brand_id', ondelete="restrict")
    issue_unknown = fields.Boolean()
    issue = fields.Text(string='Issue')
    service_template_id = fields.Many2one("vehicle.service.template")
    model = fields.Char(string='Model', related='plate_no.model')
    color = fields.Char(string='Color', related='plate_no.color')
    transmission_type = fields.Selection([("auto", "Automatic"), ("manual", "Manual")], related='plate_no.transmission_type')
    last_oil_change_date = fields.Date("Last Change Oil")
    odometer_reading = fields.Float()
    fuel_value = fields.Integer(string='Fuel Level')
    fuel_gauge = fields.Integer(related="fuel_value")
    fuel_gauge_unit = fields.Char()
    fuel_type_id = fields.Many2one('fuel.type', string='Fuel Type', related='plate_no.fuel_type_id', ondelete="restrict")
    year_of_manufacturing = fields.Char(string="Year of Manufacturing", related='plate_no.year_of_manufacturing')
    warranty_date = fields.Boolean(string='Warranty')
    insurance = fields.Boolean(string='Insurance')
    pollution = fields.Boolean(string='Pollution')
    accessories_ids = fields.One2many('vehicle.accessories', 'repair_work_order_id', ondelete="cascade",
                                      string='Accessories Available In Vehicle')
    sale_order_id = fields.Many2one("sale.order", string='Sale Oder Id', copy=False)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id)
    work_sheet_expense = fields.Float(compute="compute_repair_expense", track_visibility='onchange', store=True)
    used_part_expense = fields.Float(compute="compute_repair_expense", track_visibility='onchange', store=True)
    total_repair_untaxed_expense = fields.Float(compute="compute_repair_expense", track_visibility='onchange',
                                                store=True)
    note = fields.Text(default="Total Final Amount may vary, this is a repair work order estimate.")
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], default='0',
                                string="Priority")
    active = fields.Boolean(default=True)
    vin_no = fields.Char('VIN No', related='plate_no.vin_no')
    odo_meter_reading = fields.Char('Odo Meter Reading')
    ref = fields.Char('Reference')
    rows = fields.Integer('Rows', default=15)

    def name_get(self):
        result = []
        for rec in self:
            # Case 1: Both vehicle_src_id and cat_id are present
            if rec.plate_no.vehicle_src_id and rec.plate_no.cat_id:
                result.append((rec.id, '%s - [%s-%s-%s]' % (
                    rec.name, rec.plate_no.vehicle_src_id.name, rec.plate_no.plate_no, rec.plate_no.cat_id.name)))

            # Case 2: Only vehicle_src_id is present, but cat_id is not
            elif rec.plate_no.vehicle_src_id and not rec.plate_no.cat_id:
                result.append((rec.id, '%s - [%s-%s]' % (
                    rec.name, rec.plate_no.vehicle_src_id.name, rec.plate_no.plate_no)))

            # Case 3: Only cat_id is present, but vehicle_src_id is not
            elif rec.plate_no.cat_id and not rec.plate_no.vehicle_src_id:
                result.append((rec.id, '%s - [%s-%s]' % (
                    rec.name, rec.plate_no.plate_no, rec.plate_no.cat_id.name)))

            # Case 4: Neither vehicle_src_id nor cat_id are present
            else:
                result.append((rec.id, '%s' % (rec.name)))

        return result

    # @api.onchange("plate_no")
    # def fetch_details_by_plate(self):
    #     if self.plate_no:
    #         plate_no = self.plate_no.replace(" ", "")
    #         self.plate_no = plate_no.upper()
    #         matched_vehicle_id = self.env["vehicle.detail.by.plate"].search([("plate_no", "=ilike", self.plate_no)],
    #                                                                         limit=1)
    #         if matched_vehicle_id:
    #             self.plate_exist = True
    #             self.customer_id = matched_vehicle_id.customer_id.id
    #             # self.phone = matched_vehicle_id.phone
    #             # self.email = matched_vehicle_id.email
    #             self.vehicle_type_id = matched_vehicle_id.vehicle_type_id.id
    #             self.brand_id = matched_vehicle_id.brand_id.id
    #             self.model = matched_vehicle_id.model
    #             self.color = matched_vehicle_id.color
    #             self.transmission_type = matched_vehicle_id.transmission_type
    #             self.fuel_type_id = matched_vehicle_id.fuel_type_id.id
    #             self.year_of_manufacturing = matched_vehicle_id.year_of_manufacturing
    #         else:
    #             self.plate_exist = False

    @api.depends("work_sheet_ids.subtotal", "used_part_ids.subtotal")
    def compute_repair_expense(self):
        for rec in self:
            if rec.work_sheet_ids:
                rec.work_sheet_expense = sum(rec.work_sheet_ids.mapped("subtotal"))
            else:
                rec.work_sheet_expense = 0
            if rec.used_part_ids:
                rec.used_part_expense = sum(rec.used_part_ids.mapped("subtotal"))
            rec.total_repair_untaxed_expense = rec.work_sheet_expense + rec.used_part_expense

    @api.onchange("service_template_id")
    def fill_from_template(self):
        service_template_id = self.service_template_id

        if service_template_id:
            self.repair_team_ids = service_template_id.repair_team_ids
            work_sheet = []
            for work_id in service_template_id.work_ids:
                work_sheet.append((0, 0, {
                    "mechanic_id": work_id.mechanic_id.id,
                    "service_id": work_id.service_id.id,
                    "description": work_id.description,
                    "cost_type": work_id.cost_type,
                    "cost": work_id.cost,
                    "abstract_uom": work_id.abstract_uom,
                    "qty": work_id.qty,
                    "time": work_id.time,
                }))
            self.work_sheet_ids = [(5, _, _)]
            self.work_sheet_ids = work_sheet
        else:
            self.work_sheet_ids = [(5, _, _)]

    @api.onchange("vehicle_type_id")
    def set_brand_domain(self):
        domain = {}
        if self.vehicle_type_id:
            domain.update({"brand_id": [('id', 'in', self.vehicle_type_id.vehicle_brand_ids.ids)]})
            domain.update({"service_template_id": [('vehicle_type_id', '=', self.vehicle_type_id.id)]})
        else:
            domain.update({"brand_id": []})
            domain.update({"service_template_id": []})

        return {"domain": domain}

    @api.onchange("brand_id")
    def set_template_domain(self):
        domain = {}
        if self.brand_id and self.vehicle_type_id:
            domain.update({"service_template_id": [('vehicle_type_id', '=', self.vehicle_type_id.id),
                                                   ('vehicle_brand_id', '=', self.brand_id.id)]})
        else:
            domain.update({"service_template_id": []})
        self.service_template_id = False
        return {"domain": domain}

    @api.onchange("repair_team_ids")
    def get_team_members(self):
        self.team_member_ids = False
        self.manager_ids = False
        if self.repair_team_ids:
            team_member_ids = self.repair_team_ids.mapped("team_member_ids")
            team_leader_id = self.repair_team_ids.mapped("team_leader_id")
            self.team_member_ids = team_member_ids.ids
            self.manager_ids = team_leader_id.ids
            work_sheet = self.env['work.sheet']
            if self.work_sheet_ids:
                for line in self.work_sheet_ids:
                    if line.mechanic_id.id not in team_member_ids.ids:
                        work_sheet += line
            if work_sheet:
                self.work_sheet_ids = [(2, x,) for x in work_sheet.ids]
        else:
            self.work_sheet_ids = False

    @api.model
    def create(self, vals):
        # vals['name'] = self.env['ir.sequence'].get('vehicle.repair.work.order')
        res = super(VehicleRepairWorkOrder, self).create(vals)
        get_seq = self.env['ir.sequence'].next_by_sequence_for('vehicle_service')
        job_seq = self.env['ir.sequence'].next_by_code('job.card.seq')
        res.name = get_seq or job_seq
        return res

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def confirm_service(self):
        self.state = 'confirm'
        for repair_work_order in self.filtered(
                lambda work_order: work_order.customer_id not in work_order.message_partner_ids):
            repair_work_order.message_subscribe([repair_work_order.customer_id.id])

        self.send_email_user()

    def button_cancel(self):
        self.state = 'cancel'

    def button_draft(self):
        self.state = 'draft'

    def button_done(self):
        self.state = 'under_process'

    def button_finish(self):
        self.state = 'done'
        record_id = self.env['sale.order'].create({'partner_id': self.customer_id.id, 'order_line': self.order_line()})
        self.sale_order_id = record_id.id
        self.send_email_user()

    def order_line(self):
        res = []
        for work_line in self.work_sheet_ids:
            res.append((0, 0,
                        {
                            'product_id': work_line.service_id.id,
                            'name': work_line.description,
                            'price_unit': work_line.cost,
                            'product_uom_qty': work_line.qty
                        }))

        for used_part in self.used_part_ids:
            res.append((0, 0,
                        {
                            'product_id': used_part.part_id.id,
                            'name': used_part.description,
                            'product_uom_qty': used_part.quantity,
                            'price_unit': used_part.unit_price,
                        }))

        return res

    def sale_order_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }

    def send_email_user(self):
        res_data = self.env['ir.config_parameter'].sudo()
        send_email_confirm = res_data.get_param('vehical_repair_management.send_email_when_confirm', default=False)
        send_email_done = res_data.get_param('vehical_repair_management.send_email_when_done', default=False)
        send_email_to_customer = res_data.get_param('vehical_repair_management.send_email_when_customer_is_confirm',
                                                    default=False)

        if send_email_to_customer:
            html_body = "Dear Customer<br/>"
            html_body += "Your Vehicle Service Work Order Ref# " + str(
                self.name) + " is " + self.state + " and Vehicle Plate No is " + str(self.plate_no)
            html_body += "<br/>Check the attachment for more details.<br/><br/>Thanks<br/>Have a good day"
            self.send_email(html_body, self.customer_id)

        if send_email_confirm or send_email_done:
            user_ids = self.env.ref('vehical_repair_management.group_vehicle_repair_manager').users
            for user in user_ids:
                html_body = "Dear sir<br/>"
                html_body += "My vehicle Service Work Order Ref# " + str(
                    self.name) + " is " + self.state + " and Plate No is " + str(
                    self.plate_no) + "and fuel value  is " + str(self.fuel_value) + " and type is " + str(
                    self.fuel_type_id.name)
                if self.issue:
                    html_body += "<br/> Issue: <br/> " + str(self.issue)
                html_body += "<br/>Check the attachment for more details.<br/><br/>Thanks<br/>Have a good day"

                self.send_email(html_body, user)

    def send_email(self, html_body, user):
        pdf = self.env.ref('vehical_repair_management.action_report_drop_off_receipt')._render_qweb_pdf(self.id)[0]
        bounce_mail_values = {'body_html': html_body, 'subject': "Vehicle Service Work Order, Ref#: %s" % self.name,
                              'email_to': user.email, 'auto_delete': True, 'email_from': self.env.user.email_formatted,
                              'attachment_ids': [(0, 0, {
                                  'name': 'Vehicle Service Work Order %s' % self.name,
                                  'datas': base64.b64encode(pdf),
                                  'res_model': self._name,
                                  'res_id': self.id,
                                  'mimetype': 'application/pdf',
                                  'type': 'binary',
                                  'store_fname': 'Vehicle Service Work Order'
                              })]}

        self.env['mail.mail'].create(bounce_mail_values).send()

    # def unlink(self):
    #     for rec in self:
    #         if rec.active and rec.state in ['confirm', 'under_process', 'done']:
    #             raise UserError(_('You cannot delete a confirmed, under process or done work order.'))


class ServiceInfo(models.Model):
    _name = 'vehicle.part.used.info'

    part_id = fields.Many2one('product.product', 'Part', domain=[('type', '=', 'product')])
    description = fields.Text(string='Description',  readonly=False)
    part_name = fields.Char(string='Part Name')
    part_no = fields.Char(string='Part #')
    quantity = fields.Integer(string='Qty', default='1')
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal')
    repair_work_order_id = fields.Many2one('vehicle.repair.work.order', string='Repair Work Order')
    currency_id = fields.Many2one("res.currency", related="repair_work_order_id.currency_id")

    @api.onchange('part_id')
    def _price_unit_change(self):
        for rec in self:
            rec.unit_price = rec.part_id.lst_price

            if not rec.part_id.description:
                rec.description = f'{rec.part_id.name}'
            else:
                rec.description = f'{rec.part_id.name}\n{rec.part_id.description}'


    @api.onchange('quantity', 'unit_price')
    def _total_amount(self):
        self.subtotal = self.quantity * self.unit_price
