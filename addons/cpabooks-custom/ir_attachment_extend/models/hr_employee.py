import base64
import requests
from odoo import fields, models, api, _


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    check_image_db = fields.Boolean('Image', compute="_compute_image_db", default=False, store=True)

    @api.depends('image_1920')
    def _compute_image_db(self):
        for emp in self:
            emp.check_image_db = bool(emp.image_1920)
