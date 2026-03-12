from odoo import fields, models, api


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange('structure_id')
    def _onchange_media_id(self):
        pass
