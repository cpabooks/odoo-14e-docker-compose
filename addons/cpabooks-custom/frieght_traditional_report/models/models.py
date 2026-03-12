# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class VehicleInherit(models.Model):
    _inherit = "account.move"

    vehicle_no = fields.Char("Vehicle No.")
    vehicle_name = fields.Char("Vehicle Name")
    kilometer = fields.Char("Kilometer")

