from odoo import api, models,fields, _

class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def set_all_access(self):
        data = self.search([('name', '=', 'Signature Rule')], limit=1)
        group_ids = self.env['res.groups'].search([])

        if data:
            data.write({
                'groups': [(4, group.id) for group in group_ids]
            })

    @api.model
    def delete_rule(self):
        data = self.search([('name', '=', 'Signature Rule')], limit=1)
        if data:
            data.unlink()

    @api.model
    def action_update_rule(self):
        model_id = self.env['ir.model'].search([
            ('model', '=', 'account.account')
        ])
        vals = {
            'name': 'Account multi-company',
            'model_id': model_id.id,
            'active': True,
            'domain_force': "['|', ('company_id', '=', False), ('company_id', 'in', user.company_ids.ids)]",
            'global': True,
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': True,
        }
        rule_id = self.search([
            ('model_id', '=', model_id.id)
        ], limit=1)

        if rule_id:
            rule_id.domain_force = ''
            rule_id.write(vals)
        else:
            self.create(vals)
