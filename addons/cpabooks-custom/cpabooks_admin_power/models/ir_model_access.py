from odoo import api, models


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    def action_set_partner_access(self):
        all_partner_access = self.search([
            ('model_id.model', 'ilike', 'res.partner')
        ])
        for line in all_partner_access:
            if line.name != 'res.partner partner_access':
                line.write({
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': False,
                    'perm_unlink': False,
                })
        models = list(set([line.model_id.model for line in all_partner_access]))
        for model in models:
            model_id = self.env['ir.model'].search([
                ('model', '=', model)
            ], limit=1)
            group_id = self.env['res.groups'].search([
                ('name', 'like', 'Partner Access')
            ], limit=1)
            if model_id and group_id:
                vals = {
                    'model_id': model_id.id,
                    'name': 'res.partner partner_access',
                    'group_id': group_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                }
                get_access = self.search([
                    ('model_id.id', '=', model_id.id),
                    ('group_id.id', '=', group_id.id)
                ], limit=1)
                if not get_access:
                    self.create(vals)
                else:
                    get_access.write(vals)

    @api.model
    def action_set_product_access(self):
        get_all_product_access = self.search([
            ('model_id.model', 'ilike', 'product')
        ])
        for line in get_all_product_access:
            line.write({
                'perm_read': True,
                'perm_write': True,
                'perm_create': False,
                'perm_unlink': False,
            })

        models = list(set([line.model_id.model for line in get_all_product_access]))
        for model in models:
            model_id = self.env['ir.model'].search([
                ('model', '=', model)
            ], limit=1)
            group_id = self.env['res.groups'].search([
                ('name', 'like', 'Product Editor')
            ], limit=1)
            if model_id and group_id:
                vals = {
                    'model_id': model_id.id,
                    'name': 'product.product product_editor',
                    'group_id': group_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                }
                get_access = self.search([
                    ('model_id.id', '=', model_id.id),
                    ('group_id.id', '=', group_id.id)
                ], limit=1)
                if not get_access:
                    self.create(vals)
                else:
                    get_access.write(vals)

    @api.model
    def get_res_lang_group_all(self):
        group_id = self.search([('name', 'ilike', 'res_lang group_all')])
        if group_id:
            group_id.write({
                'perm_read': True,
                'perm_write': True,
                'perm_create': False,
                'perm_unlink': False
            })

    @api.model
    def get_bill_invoice_access(self):
        get_all_invoices_group = self.search([
            ('model_id.model', 'ilike', 'account.move')
        ])

        for i in get_all_invoices_group:
            if i.name != 'account.move invoice_bills_editor':
                i.write({
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': False,
                    'perm_unlink': False,
                })
        models = list(set([line.model_id.model for line in get_all_invoices_group]))
        for model in models:
            model_id = self.env['ir.model'].search([
                ('model', '=', model)
            ], limit=1)

            group_id = self.env['res.groups'].search([
                ('name', 'like', 'Invoice / Bills Creator')
            ], limit=1)

            if model_id and group_id:
                vals = {
                    'model_id': model_id.id,
                    'name': 'account.move invoice_bills_creator',
                    'group_id': group_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                }
                get_access = self.search([
                    ('model_id.id', '=', model_id.id),
                    ('group_id.id', '=', group_id.id)
                ], limit=1)

                if not get_access:
                    self.create(vals)
                else:
                    get_access.write(vals)

    @api.model
    def action_assign_all_users_to_invoice_access(self):
        group_id = self.env.ref('cpabooks_admin_power.group_account_move')
        users = self.env['res.users'].search([])
        if users and group_id:
            for user in users:
                user.write({
                    'groups_id': [(4, group_id.id)]
                })



