# -*- coding: utf-8 -*-
from odoo import models, fields, api
import csv
import os

class HideMenuCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        """
        Else the menu will be still hidden even after removing from the list
        """
        self.clear_caches()
        return super(HideMenuCompany, self).create(vals)

    def write(self, vals):
        """
        Else the menu will be still hidden even after removing from the list
        """
        res = super(HideMenuCompany, self).write(vals)
        for menu in self.hide_company_menu_ids:
            menu.sudo().write({
                'restrict_company_ids': [(4, self.env.company.id)]
            })
        self.clear_caches()
        return res

    def _get_is_admin(self):
        """
        The Hide specific menu tab will be hidden for the Admin user form.
        Else once the menu is hidden, it will be difficult to re-enable it.
        """
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True

    def _set_default(self):
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'hide_menu_default.csv'))
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                name = row['name']
                module = self.env['ir.module.module'].search([('state', '=', 'installed'), ('name', '=', name)],limit=1)
                if module:
                    menus_by_module = module.menus_by_module
                    if menus_by_module:
                        menu_names = menus_by_module.splitlines()
                        for menu_name in menu_names:
                            menu = self.env['ir.ui.menu'].sudo().search([('name', '=', menu_name)])
                            if not menu:
                                menu_name = menus_by_module.split('/' or '\n')
                                menu = self.env['ir.ui.menu'].sudo().search([('name', '=', menu_name[0])])
                            for res in menu:
                                if res and res not in self.hide_company_menu_ids:
                                    self.write({
                                        'hide_company_menu_ids': [(4, res.id)]
                                    })
        print('esecuted _set_default()')

    def set_default(self):
        self._set_default()
        # print(self.hide_company_menu_ids)

        for menu in self.hide_company_menu_ids:
            get_menu = self.env['ir.ui.menu'].search([('id', '=', menu.id)],limit=1)
            get_menu.write({
                'restrict_company_ids':[(4, self.env.company.id)]
            })
        # self.clear_caches()


    @api.model
    def hide_menu_default(self):
        self._set_default()

    hide_company_menu_ids = fields.Many2many('ir.ui.menu', string="Menu (Company Wise)", store=True,
                                     help='Select menu items that needs to be '
                                          'hidden to this user ')
    is_admin = fields.Boolean(compute=_get_is_admin)


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'

    restrict_company_ids = fields.Many2many('res.company', string='Restrict Company')
