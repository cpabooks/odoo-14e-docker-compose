# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_cancel(self):
        self.write({'state': 'cancel'})
        return super(HrPayslip, self).action_payslip_cancel()


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection(selection_add=[('cancel', 'Rejected')])

    def action_cancel_batch(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.write({'state': 'cancel'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: