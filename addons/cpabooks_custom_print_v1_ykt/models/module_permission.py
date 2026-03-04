import base64
import csv
import io

from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError


class ModulePermission(models.Model):
    _name="module.permission"

    permission=fields.Selection([('give_crm','Give CRM Permission'),('never_give_crm','Never Give CRM Permission')], string="Permission",required=True)
    company_id=fields.Many2one("res.company",string="Company", required=True)

    def action_permit(self):
        get_company_all_emp=self.env['res.users'].sudo().search([('company_id','=',self.company_id.id)])

        if self.permission in ('give_crm','never_give_crm'):
            group_id = self.env.ref('cpabooks_custom_print_v1_ykt.group_show_crm')

            # group=self.env['res.groups'].sudo().search([('name','=','Show Discuss App')])
            if self.permission=='give_crm':
                group_id.users = [(4, user.id) for user in get_company_all_emp]
                # group.write( {'users': [(4, user) for user in get_company_all_emp]})
            if self.permission=='never_give_crm':
                group_id.users = [(3, user.id) for user in get_company_all_emp]
                # group.write({'users': [(3, user) for user in get_company_all_emp]})


class CRMSuccessMessageWizard(models.TransientModel):
    _name = 'crm.success.message.wizard'
    _description = "Show Message"

    message = fields.Text('Message', required=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
