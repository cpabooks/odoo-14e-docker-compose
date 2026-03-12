import csv

from odoo import models, api, fields, _
import os

class UpdateMultiModule(models.Model):
    _name = 'update.multi.module'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Update Multi Modules'

    name = fields.Char('Name', default='NEW', readonly=True)
    module_id = fields.Many2one('ir.module.module', 'Module')
    module_name = fields.Char('Technical Name', related='module_id.name')
    date = fields.Date('Date', default=fields.Date.today, readonly=True)
    result_message = fields.Text('Result Message', readonly=True)
    category_id = fields.Many2one('ir.module.category', 'Category', related='module_id.category_id')
    state = fields.Selection([
        ('uninstallable', '	Uninstallable'),
        ('uninstalled', 'Not Installed'),
        ('installed', '	Installed'),
        ('to upgrade', 'To be upgraded'),
        ('to remove', 'To be removed'),
        ('to install', 'To be installed'),
    ], 'Status', related='module_id.state')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.update.multi.module') or 'NEW'
        return super(UpdateMultiModule, self).create(vals)


    @api.model
    def create_default_modules(self):

        # modules = [
        #     'professional_templates_v1',
        #     'cpabooks_chart_of_accounts_v1',
        #     'dev_company_document_expiry',
        #     'dev_employee_document_expiry',
        #     'cpabooks_tally',
        #     'cpabooks_daily_reports',
        #     'cpabooks_switchgear_custom',
        #     'cpabooks_flowchart',
        #     'cost_estimate_customer_ld',
        #     'cpabooks_flowchart',
        #     'cpabooks_switchgear_custom',
        #     'cpabooks_chart_of_accounts',
        #     'cpabooks_accounting_automation',
        #     'bi_employee_payslip_report',
        #     'account_dynamic_reports',
        #     'cpabooks_admin_power',
        #     'hr_holidays',
        #     'cpabooks_delivery_slip',
        #     'cpabooks_hr_allowance',
        #     'cpabooks_hr_extend',
        #     'cpabooks_payment_voucher',
        #     'project_task_approve',
        #     'pways_hr_sepration_management',
        #     'sh_print_lead',
        #     'tecspek_customization',
        #     'cpabooks_mej',
        #     'dev_invoice_multi_payment',
        #     'cpabooks_payroll_automation',
        #     'cpabooks_hr_payroll',
        #     'cpabooks_payroll_overtime',
        #     'bi_hr_payroll_timesheet',
        #     'dynamic_xlsx',
        #     'dynamic_xlsx-main',
        #     'automatic_backup_db',
        #     'bi_employee_advance_salary',
        #     'bi_hr_overtime_request',
        #     'bi_meeting_minutes',
        #     'bi_subtask',
        #     'skit_freeze_header',
        #     'cpabooks_bank_details',
        #     'cpabooks_custom_print',
        #     'cpabooks_item_codes',
        #     'CPAbooks_db_lock',
        #     'acc_invoice_payment_cancel_app',
        #     'allinone_print_digital_sign_app',
        #     'bi_print_journal_entries',
        #     'cpabooks_crm_extend',
        #     'cpabooks_digital_signature_pt',
        #     'cpabooks_estimation_multi',
        #     'cpabooks_hr_payroll',
        #     'cpabooks_intercompany',
        #     'cpabooks_print_payslip',
        #     'cpabooks_project_extend',
        #     'cpabooks_project_issue_note',
        #     'cpabooks_sequences',
        #     'cpabooks_signature',
        #     'eq_inventory_valuation_report',
        #     'eq_payslip_cancel',
        #     'eq_payslip_payment',
        #     'ir_attachment_s3',
        #     'ir_attachment_url',
        #     'jt_user_login_tracker',
        #     'ks_warehouse_report',
        #     'report_pdf_options',
        #     'report_pdf_options_extend',
        #     'report_xlsx',
        #     'stock_picking_cancel_extended',
        #     'stock_valuation_ledger',
        #     'web_company_color',
        #     'app_odoo_customize',
        #     'user_recent_log',
        #     'bi_inventory_adjustment_cancel_reverse',
        #     'bi_material_purchase_requisitions',
        #     'bi_order_cancel_all',
        # ]

        self_module_ids = self.env['update.multi.module'].sudo().search([]).mapped('module_id')

        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'custom_modules.csv'))
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                mod = row['module']
                module_id = self.env['ir.module.module'].search([
                    ('name', '=', mod)
                ], limit=1)

                if module_id not in self_module_ids:
                    self.create({
                        'module_id': module_id.id
                    })

    def action_update_modules(self):
        installed_modules = []
        uninstalled_modules = []
        error_update = []
        error_install = []

        # Iterate through the modules in module_ids
        # for rec in self:
        #     module_ids = rec.module_ids.mapped('module_id')
        # for module in module_ids:
        for rec in self:
            module = rec.module_id
            print(module.name)
            if module.state == 'installed':
                try:
                    self.env.cr.savepoint()  # Add a savepoint
                    module.button_immediate_upgrade()
                    installed_modules.append(f"{module.shortdesc} ({module.name})")
                except Exception as e:
                    self.env.cr.rollback()  # Roll back to the savepoint
                    error_update.append(f"{module.shortdesc} ({module.name}) - Error: {e}")

            elif module.state in ['uninstalled', 'to remove']:
                try:
                    self.env.cr.savepoint()  # Add a savepoint
                    module.button_immediate_install()
                    uninstalled_modules.append(f"{module.shortdesc} ({module.name})")
                except Exception as e:
                    self.env.cr.rollback()  # Roll back to the savepoint
                    error_install.append(f"{module.shortdesc} ({module.name}) - Error: {e}")

        # Generate the result message with installed and uninstalled modules
        result_message = ""
        if installed_modules:
            result_message += "Successfully Upgraded modules:\n" + "\n".join(installed_modules) + "\n\n"
        if uninstalled_modules:
            result_message += "Successfully Installed modules:\n" + "\n".join(uninstalled_modules) +"\n\n"
        if error_update:
            result_message += "Error while Upgrading module:\n" + "\n".join(error_update) +"\n\n"
        if error_install:
            result_message += "Error while Installing module:\n" + "\n".join(error_install)

        # Create and open the wizard to display the result message
        if result_message:
            self.update({
                'result_message': result_message
            })
            result_wizard = self.env['update.module.result.wizard'].create({
                'result_message': result_message
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'update.module.result.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('cpabooks_custom_updates.view_update_module_result_wizard').id,
                'target': 'new',
                'res_id': result_wizard.id,
            }



