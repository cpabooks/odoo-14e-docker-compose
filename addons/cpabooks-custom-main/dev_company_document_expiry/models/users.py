from odoo import api, fields, models


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def get_user_allowed_company(self):
        get_user_allowed_ids=self.env.company.id
        return [('company_id','=',get_user_allowed_ids)]