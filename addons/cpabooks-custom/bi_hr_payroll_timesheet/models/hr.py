# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def getDuration(self, payslip):
        duration = 0.0
        # employee_id = payslip['employee_id']
        # timesheets = self.env['account.analytic.line'].sudo().search(
        #     [('employee_id', '=', employee_id.id), ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to),
        #      ('validated', '=', True)])
        tsheet_obj = self.env['account.analytic.line']
        active_id = self.id
        if active_id:
            timesheets = tsheet_obj.search(
                [('employee_id', '=', active_id), ('date', '>=', payslip.date_from),
                 ('date', '<=', payslip.date_to)])
            for tsheet in timesheets:  # counting duration from timesheets
                duration += tsheet.unit_amount
            return duration
        else:
            return 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
