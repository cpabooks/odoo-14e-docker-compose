# _*_ coding:utf-8_*_
import base64

from odoo import api, fields, models, _
import logging

from odoo.exceptions import UserError
from odoo.service.server import server

_logger = logging.getLogger(__name__)


class FuelType(models.Model):
    _name = 'fuel.type'

    name = fields.Char(string='Fuel Name')


class VehicleServiceImage(models.Model):
    _name = 'vehicle.service.image'

    image = fields.Binary(string='After Service')
    registration_id = fields.Many2one('vehicle.repair.work.order', string='After Service')
    registration_id2 = fields.Many2one('vehicle.repair.work.order', string='Before Service')


class WorkSheet(models.Model):
    _name = 'work.sheet'

    mechanic_id = fields.Many2one('hr.employee', string='Mechanic', domain="[('is_mechanic','=', True)]")
    description = fields.Text(string='Description')
    repair_work_order_id = fields.Many2one('vehicle.repair.work.order', string='Repair Work Order')
    service_id = fields.Many2one('product.product', 'Service', domain=[('type', '=', 'service')])
    cost = fields.Float(string='Price')
    cost_type = fields.Selection([("fix", "FIX"), ("price_varies", "PRICE VARIES"), ("free", "FREE")],)
    abstract_uom = fields.Char()
    qty = fields.Float("Quantity", default=1)
    time = fields.Float('Work Time')
    subtotal = fields.Float(compute="compute_service_subtotal")
    currency_id = fields.Many2one("res.currency", related="repair_work_order_id.currency_id")
    sequence = fields.Integer()

    @api.depends("service_id", "cost", "qty")
    def compute_service_subtotal(self):
        for rec in self:
            if rec.cost and rec.qty:
                rec.subtotal = rec.cost * rec.qty
            else:
                rec.subtotal = 0

    # @api.onchange("mechanic_id")
    # def get_expertise_service(self):
    #     self.service_id = False
    #     if self.mechanic_id:
    #         expertise_service_ids = self.mechanic_id.expertise_service_ids
    #         vehicle_type_service_ids = self.repair_work_order_id.vehicle_type_id.service_ids
    #         common_services = set(expertise_service_ids.ids).intersection(vehicle_type_service_ids.ids)
    #         return {"domain": {
    #             "service_id": [("id", "in", list(common_services))]
    #         }}

    @api.onchange('service_id')
    def on_change_state(self):
        for record in self:
            record.description = f'{record.service_id.name}'
            print(record.service_id.name)
            print(record.description)
            if record.service_id.description:
                record.description = f'{record.service_id.name} \n {record.service_id.description}'


            if record.service_id:
                record.cost = record.service_id.list_price
                if record.service_id.uom_id:
                    record.abstract_uom = "Per " + record.service_id.uom_id.name


class VehicleAccessories(models.Model):
    _name = 'vehicle.accessories'

    name = fields.Char(string='Name')
    quantity = fields.Integer(string='Quantity')
    description = fields.Text(string='Description')
    repair_work_order_id = fields.Many2one('vehicle.repair.work.order', string='Repair Work Order')



