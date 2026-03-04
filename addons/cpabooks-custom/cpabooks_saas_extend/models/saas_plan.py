from odoo import api, fields, models

class SaasPlans(models.Model):
    _inherit = "saas.plan"

    def _get_plan_prefix(self):
        plan = self.env['saas.plan'].search([])
        plan_num = len(plan) + 1
        if plan_num > 0:
            plan_num = "0" + str(plan_num)

        return "P" + str(plan_num)

    name = fields.Char(string='Plan', required=True, default=_get_plan_prefix)
