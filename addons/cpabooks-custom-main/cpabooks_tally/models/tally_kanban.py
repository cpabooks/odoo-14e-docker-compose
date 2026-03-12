from odoo import api, models, fields, _


class CPABooksTally(models.Model):
    _name = 'trial.balance'

class CPABooksTally(models.Model):

    _name = 'cpabooks.tally'

    name = fields.Char('Name')

    def create_tally(self):
        return {
            'name': "Create",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.account',
            'view_id': self.env.ref('account.view_account_form').id,
            'target': 'new'
        }

    def chart_of_accounts(self):
        return self.env.ref('account.action_account_form').read()[0]

    def revise_chart_of_accounts(self):
        return self.env.ref('cpabooks_tally.tally_action_account_form').read()[0]

    def alter(self):
        return self.env.ref('cpabooks_tally.action_alter_wizard').read()[0]

    def accounting_vouchers(self):
        # Logic for handling Accounting Voucher button click
        return

    def inventory_vouchers(self):
        # Logic for handling Inventory Vouchers button click
        return

    def order_voucher(self):
        # Logic for handling Order Voucher button click
        return

    def payroll_voucher(self):
        # Logic for handling Payroll Voucher button click
        return

    def action_create_budgets(self):
        return {
            'name': "Create MIS Budget",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mis.budget',
            'view_id': self.env.ref('cpabooks_tally.mis_budget_form_view').id,
        }

    def action_view_budgets(self):
        return self.env.ref('cpabooks_tally.action_mis_budget').read()[0]

    def banking(self):
        # Logic for handling Banking button click
        return

    def cafm(self):
        # Logic for handling C.A.F.M button click
        return

    def trial_balance(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_tb_report').read()[0]

    def cash_flow(self):
        return self.env.ref('account_reports.action_account_report_cs').read()[0]

    def general_ledger(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_gl_report').read()[0]

    def partner_ledger(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_plg_report').read()[0]

    def partner_ageing(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_pa_report').read()[0]

    def balance_sheet(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_bs_report').read()[0]

    def profit_loss_ac(self):
        return self.env.ref('account_dynamic_reports.action_dynamic_allinone_pl_report').read()[0]

    def stock_summary(self):
        # Logic for handling Stock Summary button click
        return

    def ratio_analysis(self):
        # Logic for handling Ratio Analysis button click
        return

    def analysis_verification(self):
        # Logic for handling Analysis and Verification button click
        return

    def display(self):
        return self.env.ref('cpabooks_tally.action_trial_kanban').read()[0]

    def document_expiry_report(self):
        # Logic for handling Document Expiry Report button click
        return

    def multi_account_printing(self):
        # Logic for handling Multi Account Printing button click
        return

    def quite(self):
        # Logic for handling Quit button click
        return


