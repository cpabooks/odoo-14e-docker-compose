from odoo import api, fields, models, _


class SetCompanyPrefix(models.Model):
    _name = 'set.company.prefix'
    _description = 'Set Company Prefix for all Sequences'

    name = fields.Char('Name', default='New')
    prefix = fields.Char('Prefix')
    # company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def set_prefix(self):
        # Get the current company
        com = self.env.company

        # Define sequences to create/update
        sequences_to_create_or_update = [
            ('reconcile', 'Account Full Reconcile', 'A'),
            ('sale', 'Sale Quotation', 'QT'),
            ('outgoing', 'Sale Delivery', 'DO'),
            ('sale_invoice', 'Sale Invoice', 'INV'),
            ('credit_note', 'Credit Note', 'RINV'),
            ('purchase', 'Purchase Order', 'LPO'),
            ('incoming', 'Purchase Receipt', 'GRN'),
            ('purchase_bill', 'Purchase Bill', 'BILL'),
            ('debit_note', 'Debit Note', 'RBILL'),
            ('internal', 'Internal Transfer', 'INT'),
            ('payment_voucher', 'Payment Voucher', 'PV'),
            ('receipt_voucher', 'Receipt Voucher', 'RV'),
            ('journal_voucher', 'Journal Voucher', 'JV'),
            ('crm', 'CRM', 'CRM'),
            ('job_estimation', 'Job Estimation', 'EST'),
            ('job_order', 'Job Order', 'JO'),
            ('project', 'Project', 'JOB'),
            ('bom', 'Bill of Material', 'BoM'),
            ('manufacturing', 'Manufacturing Orders', 'MO'),
            ('quality_chk', 'Quality Check', 'QC'),
            ('daily_site_report', 'Daily Site Report', 'DR'),
            ('weekly_site_report', 'Weekly Site Report', 'WR'),
            ('monthly_site_report', 'Monthly Site Report', 'MR'),
            ('supervisor_daily_report', 'Supervisor Daily Report', 'DSR'),
            ('supervisor_weekly_report', 'Supervisor Weekly Report', 'WSR'),
            ('supervisor_monthly_report', 'Supervisor Monthly Report', 'MSR'),
            ('client_report', 'Client Report', 'CR'),
            ('helpdesk_ticket', 'Helpdesk Ticket', 'HT'),
            ('pdc_payment', 'PDC Payment Voucher', 'PDP'),
            ('pdc_receipt', 'PDC Receipt Voucher', 'PDR')
        ]

        for sequence_for, name, code in sequences_to_create_or_update:
            # Search for existing sequence
            existing_seq = self.env['ir.sequence'].sudo().search([
                ('sequence_for', '=', sequence_for),
                ('company_id', '=', com.id)
            ])

            # Update the prefix if sequence exists
            if existing_seq:
                existing_seq.write({
                    'prefix': f'{code}/{self.prefix}/%(year)s/'
                })
            else:
                # Create a new sequence if it doesn't exist
                vals = {
                    'name': name,
                    'sequence_for': sequence_for,
                    'company_id': com.id,
                    'prefix': f'{code}/{self.prefix}/%(year)s/',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                self.env['ir.sequence'].sudo().create(vals)