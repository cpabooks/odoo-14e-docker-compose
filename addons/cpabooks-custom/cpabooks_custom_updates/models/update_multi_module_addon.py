import csv
import os
from odoo import api, models, fields, _

class UpdateMultiModuleAddon(models.Model):
    _name = 'update.multi.module.addon'
    _description = 'Update Multi Module Addon'

    @api.onchange('module_id')
    def get_fields_vals(self):
        for rec in self:
            if rec.module_id:
                rec.module_name = rec.module_id.name
                rec.category_id = rec.module_id.category_id.id
                rec.state = rec.module_id.state

    name = fields.Char('Name', default='NEW', readonly=True)
    module_id = fields.Many2one('ir.module.module', 'Module')
    module_name = fields.Char('Technical Name')
    date = fields.Date('Date', default=fields.Date.today, readonly=True)
    result_message = fields.Text('Result Message', readonly=True)
    category_id = fields.Many2one('ir.module.category', 'Category')
    state = fields.Selection([
        ('uninstallable', '	Uninstallable'),
        ('uninstalled', 'Not Installed'),
        ('installed', '	Installed'),
        ('to upgrade', 'To be upgraded'),
        ('to remove', 'To be removed'),
        ('to install', 'To be installed'),
    ], 'Status')


    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """
         Added name_search for purpose to search by name and rent type
        """
        args += ['|', ('name', operator, name), ('module_name', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.update.multi.module.addon') or 'NEW'
        return super(UpdateMultiModuleAddon, self).create(vals)


    @api.model
    def create_default_addon_modules(self):
        self_module_ids = self.env['update.multi.module.addon'].sudo().search([]).mapped('module_id')
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'addons_modules.csv'))
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                mod = row['module']
                module_id = self.env['ir.module.module'].search([
                    ('name', '=', mod)
                ], limit=1)
                vals = {}
                if module_id:
                    vals.update({
                        'module_id': module_id.id,
                        'module_name': module_id.name,
                        'category_id': module_id.category_id.id,
                        'state': module_id.state,
                    })

                if module_id not in self_module_ids:
                    self.create(vals)
                if module_id in self_module_ids:
                    module = self.env['update.multi.module.addon'].search([('module_id', '=', module_id.id)])
                    module.write(vals)

    def action_update_addons_modules(self):
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


