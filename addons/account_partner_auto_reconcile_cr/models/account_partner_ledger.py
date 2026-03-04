# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models,api,fields,_


class ReportPartnerLedger(models.AbstractModel):
    
    _inherit = "account.partner.ledger"
    
    def _get_reports_buttons(self):
        res = super(ReportPartnerLedger, self)._get_reports_buttons()
        if self.env.user.has_group('account.group_account_user') and self.env.user.company_id.account_partner_ledger_auto_reconcile:
            res.append({'name': _('Auto Reconcile'), 'action': 'partner_auto_reconcile', 'sequence': 8})
        return res
    
    
    def partner_auto_reconcile(self, options):
        all_lines = self._get_lines(options,None)
        partner_list = []
        account_reconcilation_obj = self.env['account.reconciliation.widget']
        
        for line in all_lines:
            if line.get('partner_id') and line.get('partner_id') not in partner_list:
                partner_list.append(line.get('partner_id'))
        
        for partner in partner_list:
            #Partner Receivable Account Reconcilation
            rec_manual_reconcilation_data = account_reconcilation_obj.get_data_for_manual_reconciliation('partner',[partner],'receivable')
            if rec_manual_reconcilation_data and rec_manual_reconcilation_data[0].get('account_id'):
                rec_account_id = rec_manual_reconcilation_data[0].get('account_id')
                rec_move_lines = account_reconcilation_obj.get_move_lines_for_manual_reconciliation(rec_account_id,partner)
                if rec_move_lines:
                    rec_move_line_ids = []
                    for ml in rec_move_lines:
                        rec_move_line_ids.append(ml.get('id'))
                        
                    rec_invoice_lines = self.env['account.move.line'].browse(rec_move_line_ids).filtered(lambda m :m.move_id.move_type != 'entry').sorted('id').ids
                    rec_move_lines = self.env['account.move.line'].browse(rec_move_line_ids).filtered(lambda m :m.move_id.move_type == 'entry').sorted('id').ids
                    rec_sorted_move_lines = rec_invoice_lines + rec_move_lines
                    account_reconcilation_obj.process_move_lines([{
                        'id': partner,
                        'type': 'partner',
                        'mv_line_ids': rec_sorted_move_lines,
                        'new_mv_line_dicts': [],
                    }])
                    
            #Partner Payable Account Reconcilation
            pay_manual_reconcilation_data = account_reconcilation_obj.get_data_for_manual_reconciliation('partner',[partner],'payable')
            if pay_manual_reconcilation_data and pay_manual_reconcilation_data[0].get('account_id'):
                pay_account_id = pay_manual_reconcilation_data[0].get('account_id')
                pay_move_lines = account_reconcilation_obj.get_move_lines_for_manual_reconciliation(pay_account_id,partner)
                if pay_move_lines:
                    pay_move_line_ids = []
                    
                    for ml in pay_move_lines:
                        pay_move_line_ids.append(ml.get('id'))
                        
                    pay_invoice_lines = self.env['account.move.line'].browse(pay_move_line_ids).filtered(lambda m :m.move_id.move_type != 'entry').sorted('id').ids
                    pay_move_lines = self.env['account.move.line'].browse(pay_move_line_ids).filtered(lambda m :m.move_id.move_type == 'entry').sorted('id').ids
                    
                    pay_sorted_move_lines = pay_invoice_lines + pay_move_lines
                    
                    account_reconcilation_obj.process_move_lines([{
                        'id': partner,
                        'type': 'partner',
                        'mv_line_ids': pay_sorted_move_lines,
                        'new_mv_line_dicts': [],
                    }])
        return True