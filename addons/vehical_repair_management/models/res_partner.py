from odoo import api, models, fields, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many('vehicle.detail.by.plate', 'customer_id', 'Cars')

