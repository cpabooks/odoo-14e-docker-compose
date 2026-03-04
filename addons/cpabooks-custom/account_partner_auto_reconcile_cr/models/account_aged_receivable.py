# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models,api,fields,_


class ReportAccountAgedReceivable(models.Model):
    
    _inherit = "account.aged.receivable"
    
    
    def _get_reports_buttons(self):
        res = super(ReportAccountAgedReceivable, self)._get_reports_buttons()
        if self.env.user.has_group('account.group_account_user') and self.env.user.company_id.account_aged_receivable_auto_reconcile:
            res.append({'name': _('Auto Reconcile'), 'action': 'partner_auto_reconcile', 'sequence': 8})
        return res
    
    
    def partner_auto_reconcile(self, options):
        all_lines = self._get_lines(options,None)
        partner_list = []
        account_reconcilation_obj = self.env['account.reconciliation.widget']
        
        for line in all_lines:
            p_id = line.get('id')
            if line.get('id') and 'partner_id-' in str(p_id) and int(p_id.split('-')[1]) not in partner_list:
                partner_list.append(int(p_id.split('-')[1]))
        for partner in partner_list:
            manual_reconcilation_data = account_reconcilation_obj.get_data_for_manual_reconciliation('partner',[partner],'receivable')
            if manual_reconcilation_data and manual_reconcilation_data[0].get('account_id'):
                account_id = manual_reconcilation_data[0].get('account_id')
                all_move_lines = account_reconcilation_obj.get_move_lines_for_manual_reconciliation(account_id,partner)
                if all_move_lines:
                    all_move_line_ids = []
                    for ml in all_move_lines:
                        all_move_line_ids.append(ml.get('id'))
                    invoice_lines = self.env['account.move.line'].browse(all_move_line_ids).filtered(lambda m :m.move_id.move_type != 'entry').sorted('id').ids
                    move_lines = self.env['account.move.line'].browse(all_move_line_ids).filtered(lambda m :m.move_id.move_type == 'entry').sorted('id').ids
                    sorted_move_lines = invoice_lines + move_lines
                    account_reconcilation_obj.process_move_lines([{
                        'id': partner,
                        'type': 'partner',
                        'mv_line_ids': sorted_move_lines,
                        'new_mv_line_dicts': [],
                    }])
        return True