from odoo import fields, models, api


class AdminPowerGroup(models.Model):
    _inherit = "res.groups"

    @api.model
    def action_create_admin_power(self):
        get_all_company=self.env['res.company'].sudo().search([])
        get_admin_power_group = self.env['res.groups'].sudo().search([('name','=ilike','admin power')])
        group_create=[]
        if not get_admin_power_group:
            model_access=[
                {
                    'name':'Document Layout',
                    'model_id':self.env['ir.model'].sudo().search([('model','=','base.document.layout')]).id,
                    'perm_read':True,
                    'perm_write':True,
                    'perm_create':True,
                    'perm_unlink':True
                },{
                    'name': 'Paper Format',
                    'model_id': self.env['ir.model'].sudo().search([('model', '=', 'report.paperformat')]).id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                },{
                    'name': 'Sequences',
                    'model_id': self.env['ir.model'].sudo().search([('model', '=', 'ir.sequence')]).id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                }, {
                    'name': 'View',
                    'model_id': self.env['ir.model'].sudo().search([('model', '=', 'ir.ui.view')]).id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True
                }
            ]
            model_access_create=self.env['ir.model.access'].sudo().create(model_access)
            vals={
                'name':'Admin Power',
                'category_id':self.env['ir.module.category'].sudo().search([('name','=','Administration')],limit=1,order='sequence desc').id,
                'menu_access':[(6,0,self.env['ir.ui.menu'].sudo().search([('name','in',('Users & Companies','Paper Format','Signature Setup','Re-Sequences','Company Properties'))]).ids)],
                'view_access':[(6,0,self.env['ir.ui.view'].sudo().search([('name','=','Document Layout')]).ids)],
                'model_access': [(6,0,model_access_create.ids)]

            }
            # 'model_access': model_access_create
            admin_group=self.env['res.groups'].sudo().create(vals)
            return admin_group
        else:
            # if self.menu_access:
            get_menus=self.env['ir.ui.menu'].sudo().search([('name','in',('Users & Companies','Paper Format','Signature Setup','Re-Sequences','Company Properties'))])
            for menu in get_menus:
                if menu.id not in get_admin_power_group.menu_access.ids:
                    get_admin_power_group.menu_access+=menu
            get_views=self.env['ir.ui.view'].sudo().search([('name','=','Document Layout')])
            for view in get_views:
                if view.id not in get_admin_power_group.view_access.ids:
                    get_admin_power_group.view_access+=view

            get_models=self.env['ir.model'].sudo().search([('model', 'in', ('ir.ui.view','ir.sequence','report.paperformat','base.document.layout',))])
            for model in get_models:
                if model.id not in get_admin_power_group.model_access.model_id.ids:
                    model_access_create = self.env['ir.model.access'].sudo().create({
                        'name': model.name,
                        'model_id': model.id,
                        'perm_read': True,
                        'perm_write': True,
                        'perm_create': True,
                        'perm_unlink': True
                    })
                    get_admin_power_group.model_access+=model_access_create


