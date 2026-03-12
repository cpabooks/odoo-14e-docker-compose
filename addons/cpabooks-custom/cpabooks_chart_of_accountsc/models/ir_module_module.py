from odoo import models, api, fields, _


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def button_immediate_upgrade(self):
        """Override the method to update another module when this module is updated."""
        res = super(IrModuleModule, self).button_immediate_upgrade()

        if self.name == 'cpabooks_chart_of_accounts':
            # List of modules to update/install
            modules = [
                'cpabooks_accounting_automation',
                'cpabooks_sequences',
                'cpabooks_tally',
                'cpabooks_chart_of_accounts_v1',
                'account_dynamic_reports',
                'dynamic_xlsx',
                'bi_employee_payslip_report',
            ]
            for mod in modules:
                other_module = self.env['ir.module.module'].search([
                    ('name', '=', mod)
                ], limit=1)

                if other_module:
                    if other_module.state == 'installed':
                        other_module.button_immediate_upgrade()
                        print(f'Upgraded: {other_module.shortdesc} ({other_module.name})')
                    elif other_module.state in ['uninstalled', 'to remove']:
                        other_module.button_immediate_install()
                        print(f'Installed: {other_module.shortdesc} ({other_module.name})')
                else:
                    # Log or handle cases where the module record doesn't exist
                    print(f'Module {mod} not found in the system.')

        return res
