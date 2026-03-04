from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import logging
from datetime import date, datetime
_logger = logging.getLogger(__name__)
class SequenceInheritance(models.Model):
    _inherit = 'ir.sequence'

    # is_journals=fields.Boolean(string="IS Journal Entries Sequences")
    sequence_pattern=fields.Selection([('year','Year'),
                                       ('month_year','Month With Year'),
                                       ('no_month_year','Without Year Month'),
                                       ('year_yearly','Year(Yearly)'),
                                       ('month_year_monthly','Month With Year(Monthly)'),],string="Sequence Contains",default="year_yearly")
    sequence_for=fields.Selection([('sale','Sale Quotation'),
                                   ('outgoing', 'Sale Delivery'),
                                   ('sale_invoice', 'Sale Invoice'),
                                   ('credit_note', 'Credit Note'),

                                   ('purchase','Purchase Order'),
                                   ('incoming', 'Purchase Receipt'),
                                   ('purchase_bill','Purchase Bill'),
                                   ('debit_note', 'Debit Note'),

                                   ('internal', 'Internal Transfer'),
                                   ('reconcile','Account Full Reconcile'),
                                   ('payment_voucher','Payment Voucher'),
                                   ('receipt_voucher','Receipt Voucher'),
                                   ('journal_voucher','Journal Voucher'),
                                   ('pdc_payment','PDC Payment Voucher'),
                                   ('pdc_receipt','PDC Receipt Voucher'),

                                   ('crm','CRM'),
                                   ('job_estimation','Job Estimation'),
                                   ('job_order', 'Job order'),

                                   ('bom','Bill of Material'),
                                   ('manufacturing','Manufacturing Orders'),
                                   ('project', 'Project'),
                                   ('quality_chk', 'Quality Check'),

                                   ('daily_site_report', 'Daily Site Report'),
                                   ('weekly_site_report', 'Weekly Site Report'),
                                   ('monthly_site_report', 'Monthly Site Report'),

                                   ('supervisor_daily_report', 'Supervisor Daily Report'),
                                   ('supervisor_weekly_report', 'Supervisor Weekly Report'),
                                   ('supervisor_monthly_report', 'Supervisor Monthly Report'),

                                   ('client_report', 'Client Report'),
                                   ('helpdesk_ticket','Helpdesk Ticket'),
                                   ],string="Sequence For")
    sequence_for_journals=fields.Many2one('account.journal',domain=lambda self:[('id','in',self.env['account.journal'].search([('type','not in',('sale','purchase','bank','cash'))]).ids)],check_company=True, string="Sequence For Payment/Journals")

    def set_prefix(self):
        return self.env.ref('cpabooks_sequences.set_company_prefix_wizard').read()[0]

    # ('journal_entry', 'Journal Entry')
    @api.onchange('sequence_pattern')
    def _set_sequence_pattern(self):
        for rec in self:
            if len(rec.ids)>0:
                if rec.sequence_pattern=='year' or rec.sequence_pattern=='year_yearly':
                    if '/%(year)s/%(month)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(year)s/%(month)s/','/%(year)s/')
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(year)s/' in rec.prefix:
                        continue
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(month)s/' in rec.prefix:
                        rec.prefix = rec.prefix.replace('/%(month)s/', '/%(year)s/')
                    else:
                        rec.prefix+='%(year)s/'
                elif rec.sequence_pattern=='month_year' or rec.sequence_pattern=='month_year_monthly':
                    if '/%(year)s/%(month)s/' in rec.prefix:
                        continue
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(year)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(year)s/','/%(year)s/%(month)s/')
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(month)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(month)s/','/%(year)s/%(month)s/')
                    else:
                        rec.prefix+='%(year)s/%(month)s/'
                elif rec.sequence_pattern=='no_month_year':
                    if '/%(year)s/%(month)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(year)s/%(month)s/','/')
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(year)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(year)s/','/')
                    elif '/%(year)s/%(month)s/' not in rec.prefix and '/%(month)s/' in rec.prefix:
                        rec.prefix=rec.prefix.replace('/%(month)s/','/')
                    else:
                        continue

                else:
                    continue


    @api.model
    def action_create_sequence(self):

        get_all_company = self.env['res.company'].sudo().search([])
        for com in get_all_company:
            val_list = []
            # ************************DELETE BANK CASH JOURNAL SEQUENCE***************************
            get_all_null_company = self.env['ir.sequence'].search([('company_id','=',False)])
            if get_all_null_company:
                get_all_null_company.company_id = com.id
            get_null_code_sequences = self.env['ir.sequence'].search(
                [('sequence_for', '=', None), ('code', '=', None), ('company_id', '=', com.id)])
            if get_null_code_sequences:
                get_null_code_sequences.unlink()
            get_bank_cash_journals = self.env['account.journal'].search(
                [('type', 'in', ('bank', 'cash', 'general')), ('company_id', '=', com.id)])
            for bcj in get_bank_cash_journals:
                get_sequence_for_bank_cash = self.env['ir.sequence'].sudo().search([('sequence_for_journals', '=',
                                                                                     self.env['account.journal'].search(
                                                                                         [('name', '=', bcj.name), (
                                                                                         'company_id', '=',
                                                                                         com.id)]).id),
                                                                                    ('company_id', '=', com.id)])
                if get_sequence_for_bank_cash:
                    get_sequence_for_bank_cash.unlink()
            # ************************DELETE BANK CASH JOURNAL SEQUENCE***************************
            # get_journals=self.env['account.journal'].search([('type','not in',('sale','purchase','bank','cash')),('company_id','=',com.id)])
            # for journal in get_journals:
            #     get_journal_seq=self.env['ir.sequence'].sudo().search([('sequence_for_journals','=',
            #                             self.env['account.journal'].search([('name','=',journal.name),('company_id','=',com.id)]).id),('company_id','=',com.id)])
            #     if not get_journal_seq:
            #         vals = {
            #             'name': journal.name,
            #             'sequence_for_journals': self.env['account.journal'].search([('name','=',journal.name),('company_id','=',com.id)]).id,
            #             'company_id': com.id,
            #             'prefix': 'CO' + str(com.id) + '/'+journal.code+'/%(year)s/',
            #             'padding': 5,
            #             'number_increment': 1,
            #             'number_next_actual': 1
            #         }
            #         val_list.append(vals)
            get_acc_reconcile_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'reconcile'), ('company_id', '=', com.id)])

            if not get_acc_reconcile_seq:
                vals = {
                    'name': 'Account Full Reconcile',
                    'sequence_for': 'reconcile',
                    'company_id': com.id,
                    'prefix': 'A',
                    'padding': 0,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_sale_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'sale'), ('company_id', '=', com.id)])
            if not get_sale_seq:
                vals = {
                    'name': 'Sale Qutotation',
                    'sequence_for': 'sale',
                    'company_id': com.id,
                    'prefix': 'QT/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_do_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'outgoing'), ('company_id', '=', com.id)])
            if not get_do_seq:
                vals = {
                    'name': 'Sale Delivery',
                    'sequence_for': 'outgoing',
                    'company_id': com.id,
                    'prefix': 'DO/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_inv_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'sale_invoice'), ('company_id', '=', com.id)])
            if not get_inv_seq:
                vals = {
                    'name': 'Sale Invoice',
                    'sequence_for': 'sale_invoice',
                    'company_id': com.id,
                    'prefix': 'INV/' + 'CO' + str(com.id) + '/%(year)s/%(month)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'sequence_pattern': 'month_year_monthly'
                }
                val_list.append(vals)

            get_inv_return_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'credit_note'), ('company_id', '=', com.id)])
            if not get_inv_return_seq:
                vals = {
                    'name': 'Credit Note',
                    'sequence_for': 'credit_note',
                    'company_id': com.id,
                    'prefix': 'RINV/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_lpo_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'purchase'), ('company_id', '=', com.id)])
            if not get_lpo_seq:
                vals = {
                    'name': 'Purchase Order',
                    'sequence_for': 'purchase',
                    'company_id': com.id,
                    'prefix': 'LPO/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_grn_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'incoming'), ('company_id', '=', com.id)])
            if not get_grn_seq:
                vals = {
                    'name': 'Purchase Receipt',
                    'sequence_for': 'incoming',
                    'company_id': com.id,
                    'prefix': 'GRN/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_bill_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'purchase_bill'), ('company_id', '=', com.id)])
            if not get_bill_seq:
                vals = {
                    'name': 'Purchase Bill',
                    'sequence_for': 'purchase_bill',
                    'company_id': com.id,
                    'prefix': 'BILL/' + 'CO' + str(com.id) + '/%(year)s/%(month)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'sequence_pattern': 'month_year_monthly'
                }
                val_list.append(vals)

            get_bill_return_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'debit_note'), ('company_id', '=', com.id)])
            if not get_bill_return_seq:
                vals = {
                    'name': 'Debit Note',
                    'sequence_for': 'debit_note',
                    'company_id': com.id,
                    'prefix': 'RBILL/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_transfer_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'internal'), ('company_id', '=', com.id)])
            if not get_transfer_seq:
                vals = {
                    'name': 'Internal Transfer',
                    'sequence_for': 'internal',
                    'company_id': com.id,
                    'prefix': 'INT/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_payment_voucher_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'payment_voucher'), ('company_id', '=', com.id)])
            if not get_payment_voucher_seq:
                vals = {
                    'name': 'Payment Voucher',
                    'sequence_for': 'payment_voucher',
                    'company_id': com.id,
                    'prefix': 'PV/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_receipt_voucher_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'receipt_voucher'), ('company_id', '=', com.id)])
            if not get_receipt_voucher_seq:
                vals = {
                    'name': 'Receipt Voucher',
                    'sequence_for': 'receipt_voucher',
                    'company_id': com.id,
                    'prefix': 'RV/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_journal_voucher_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'journal_voucher'), ('company_id', '=', com.id)])
            if not get_journal_voucher_seq:
                vals = {
                    'name': 'Journal Voucher',
                    'sequence_for': 'journal_voucher',
                    'company_id': com.id,
                    'prefix': 'JV/' + 'CO' + str(com.id) + '/%(year)s/%(month)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'sequence_pattern': 'month_year_monthly'
                }
                val_list.append(vals)

            get_crm_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'crm'), ('company_id', '=', com.id)])
            if not get_crm_seq:
                vals = {
                    'name': 'CRM',
                    'sequence_for': 'crm',
                    'company_id': com.id,
                    'prefix': 'CRM/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_job_estimate_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'job_estimation'), ('company_id', '=', com.id)])
            if not get_job_estimate_seq:
                vals = {
                    'name': 'Job Estimation',
                    'sequence_for': 'job_estimation',
                    'company_id': com.id,
                    'prefix': 'EST/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_job_order_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'job_order'), ('company_id', '=', com.id)])
            if not get_job_order_seq:
                vals = {
                    'name': 'Job Order',
                    'sequence_for': 'job_order',
                    'company_id': com.id,
                    'prefix': 'JO/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_project_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'project'), ('company_id', '=', com.id)])
            if not get_project_seq:
                vals = {
                    'name': 'Project',
                    'sequence_for': 'project',
                    'company_id': com.id,
                    'prefix': 'JOB/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_bom_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'bom'), ('company_id', '=', com.id)])
            if not get_bom_seq:
                vals = {
                    'name': 'Bill of Material',
                    'sequence_for': 'bom',
                    'company_id': com.id,
                    'prefix': 'BoM/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_manufacturing_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'manufacturing'), ('company_id', '=', com.id)])
            if not get_manufacturing_seq:
                vals = {
                    'name': 'Manufacturing Orders',
                    'sequence_for': 'manufacturing',
                    'company_id': com.id,
                    'prefix': 'MO/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_quality_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'quality_chk'), ('company_id', '=', com.id)])
            if not get_quality_seq:
                vals = {
                    'name': 'Quality Check',
                    'sequence_for': 'quality_chk',
                    'company_id': com.id,
                    'prefix': 'QC/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_daily_site_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'daily_site_report'), ('company_id', '=', com.id)])
            if not get_daily_site_report_seq:
                vals = {
                    'name': 'Daily Site Report',
                    'sequence_for': 'daily_site_report',
                    'company_id': com.id,
                    'prefix': 'DR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_weekly_site_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'weekly_site_report'), ('company_id', '=', com.id)])
            if not get_weekly_site_report_seq:
                vals = {
                    'name': 'Weekly Site Report',
                    'sequence_for': 'weekly_site_report',
                    'company_id': com.id,
                    'prefix': 'WR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_monthly_site_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'monthly_site_report'), ('company_id', '=', com.id)])
            if not get_monthly_site_report_seq:
                vals = {
                    'name': 'Monthly Site Report',
                    'sequence_for': 'monthly_site_report',
                    'company_id': com.id,
                    'prefix': 'MR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_supervisor_daily_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'supervisor_daily_report'), ('company_id', '=', com.id)])
            if not get_supervisor_daily_report_seq:
                vals = {
                    'name': 'Supervisor Daily Report',
                    'sequence_for': 'supervisor_daily_report',
                    'company_id': com.id,
                    'prefix': 'DSR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_supervisor_weekly_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'supervisor_weekly_report'), ('company_id', '=', com.id)])
            if not get_supervisor_weekly_report_seq:
                vals = {
                    'name': 'Supervisor Weekly Report',
                    'sequence_for': 'supervisor_weekly_report',
                    'company_id': com.id,
                    'prefix': 'WSR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_supervisor_monthly_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'supervisor_monthly_report'), ('company_id', '=', com.id)])
            if not get_supervisor_monthly_report_seq:
                vals = {
                    'name': 'Supervisor Monthly Report',
                    'sequence_for': 'supervisor_monthly_report',
                    'company_id': com.id,
                    'prefix': 'MSR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_client_report_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'client_report'), ('company_id', '=', com.id)])
            if not get_client_report_seq:
                vals = {
                    'name': 'Client Report',
                    'sequence_for': 'client_report',
                    'company_id': com.id,
                    'prefix': 'CR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_acc_reconcile_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'helpdesk_ticket'), ('company_id', '=', com.id)])

            if not get_acc_reconcile_seq:
                vals = {
                    'name': 'Helpdesk Ticket',
                    'sequence_for': 'helpdesk_ticket',
                    'company_id': com.id,
                    'prefix': 'HT/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_pdc_payment_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'pdc_payment'), ('company_id', '=', com.id)])
            if not get_pdc_payment_seq:
                vals = {
                    'name': 'PDC Payment Voucher',
                    'sequence_for': 'pdc_payment',
                    'company_id': com.id,
                    'prefix': 'PDP/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            get_pdc_receipt_seq = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'pdc_receipt'), ('company_id', '=', com.id)])
            if not get_pdc_receipt_seq:
                vals = {
                    'name': 'PDC Receipt Voucher',
                    'sequence_for': 'pdc_receipt',
                    'company_id': com.id,
                    'prefix': 'PDR/' + 'CO' + str(com.id) + '/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                val_list.append(vals)

            self.create(val_list)

    @api.model
    def next_by_sequence_for(self, sequence_for,hint=None, sequence_date=None):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.
        """
        print(f'next_by_sequence_for {sequence_date}')
        self.check_access_rights('read')
        company_id = self.env.company.id
        seq_ids = self.search([('sequence_for', '=', sequence_for), ('company_id', 'in', [company_id, False])],limit=1,
                              order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_for)
            return False
        seq_id = seq_ids[0]
        result = seq_id._next(sequence_date=sequence_date)
        print(f'result next seqL {result}')
        return result

    def get_next_char(self, number_next):
        res = super(SequenceInheritance, self).get_next_char(number_next)
        print(f'get_next_char {res}')
        return res

    def next_by_sequence_for_journal(self, sequence_for, sequence_date=None):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.
        """
        self.check_access_rights('read')
        company_id = self.env.company.id
        seq_ids = self.search([('sequence_for_journals', '=', sequence_for), ('company_id', 'in', [company_id, False])],limit=1,
                              order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_for)
            return False
        seq_id = seq_ids[0]
        return seq_id._next(sequence_date=sequence_date)

    @api.model
    def create(self, vals_list):
        if 'sequence_for' in vals_list.keys() and vals_list['sequence_for']!=False:
            get_exists_one=self.env['ir.sequence'].sudo().search([('company_id','=',vals_list['company_id']),('sequence_for','=',vals_list['sequence_for'])],limit=1)
            if get_exists_one:
                raise ValidationError(_("Already sequence for '%s' is created for company '%s'" %(get_exists_one.sequence_for,get_exists_one.company_id.name)))
            # else:
            #     res = super(SequenceInheritance, self).create(vals_list)
        # if 'sequence_for_journals' in vals_list.keys() and vals_list['sequence_for_journals']!=False:
        #     get_exists_one=self.env['ir.sequence'].sudo().search([('company_id','=',vals_list['company_id']),('sequence_for_journals','=',vals_list['sequence_for_journals'])],limit=1)
        #     if get_exists_one:
        #         raise ValidationError(_("Already sequence for '%s' is created for company '%s'" %(get_exists_one.sequence_for,get_exists_one.company_id.name)))
        #     # else:
        #     #     res = super(SequenceInheritance, self).create(vals_list)
        # # else:
        res=super(SequenceInheritance, self).create(vals_list)
        return res

    @api.onchange('sequence_for')
    def existency_chk(self):
        if  self.sequence_for!=False:
            # self.sequence_for_journals=False
            get_exists_one = self.env['ir.sequence'].sudo().search(
                [('company_id', '=', self.company_id.id), ('sequence_for', '=', self.sequence_for)], limit=1)
            if get_exists_one:
                raise ValidationError(_("Already sequence for this type is created for company '%s'" % (
                 get_exists_one.company_id.name)))

    # @api.onchange('sequence_for_journals')
    # def existency_journals_chk(self):
    #     if self.sequence_for_journals:
    #         # self.sequence_for=False
    #         get_exists_one = self.env['ir.sequence'].sudo().search(
    #             [('company_id', '=', self.company_id.id), ('sequence_for_journals', '=', self.sequence_for_journals.id)], limit=1)
    #         if get_exists_one:
    #             raise ValidationError(_("Already sequence for this type is created for company '%s'" % (
    #                 get_exists_one.company_id.name)))

    @api.model
    def next_by_custom_seq(self, sequence_for=False, field_date=False, next_number=False):
        # Search for the sequence
        print(sequence_for)
        seq_id = self.search([
            ('sequence_for', '=', sequence_for),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        # Handle prefix and next number
        seq_prefix = seq_id.prefix or ""
        if not next_number:
            next_number = seq_id.number_next_actual
        padding = seq_id.padding

        # Ensure field_date is set, default to today's date
        if not field_date:
            field_date = date.today()

        # If field_date is a string, ensure it is parsed correctly
        if isinstance(field_date, str):
            try:
                # Handle both formats: YYYY-MM-DD and DD/MM/YYYY
                if "-" in field_date:
                    date_obj = datetime.strptime(field_date, "%Y-%m-%d")
                else:
                    date_obj = datetime.strptime(field_date, "%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Invalid date format: {field_date}. Expected formats: 'YYYY-MM-DD' or 'DD/MM/YYYY'.")
        else:
            # If already a `date` object, no need to parse
            date_obj = field_date

        # Extract day, month, and year
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year

        # Replace placeholders in the sequence prefix
        if "%(year)s" in seq_prefix:
            seq_prefix = seq_prefix.replace("%(year)s", str(year))
        if "%(month)s" in seq_prefix:
            seq_prefix = seq_prefix.replace("%(month)s", f"{month:02d}")
        if "%(day)s" in seq_prefix:
            seq_prefix = seq_prefix.replace("%(day)s", f"{day:02d}")

        seq = f'{seq_prefix}{str(next_number).zfill(padding)}'
        return seq


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    def sequence_domain(self):
        return [('company_id','=',self.env.company.id)]
