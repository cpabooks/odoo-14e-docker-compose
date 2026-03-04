from odoo import models
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        for payslip in self:
            hr_payslip = self.env['hr.payslip'].search(
                [('employee_id', '=', payslip.employee_id.id), ('date_from', '>=', payslip.date_from),
                 ('date_to', '<=', payslip.date_to), ('state', '=', 'done')])
            if hr_payslip:
                raise UserError(("%s has done payslip on same period" % self.employee_id.name))
        return super(HrPayslip, self).action_payslip_done()

    def action_payslip_cancel(self):
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()
