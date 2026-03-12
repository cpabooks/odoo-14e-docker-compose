from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_company(self):
        return [('company_id','in',self.env.company.ids)]