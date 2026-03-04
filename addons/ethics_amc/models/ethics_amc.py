# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    amc_id = fields.Many2one("ethics.amc", string="AMC")


class EthicsAmc(models.Model):
    _name = "ethics.amc"
    _description = 'AMC'

    @api.depends('invoice_ids')
    def _compute_invoice(self):
        for amc in self:
            if amc.invoice_ids:
                amc.invoice_count = len(amc.invoice_ids.ids)
                amc.is_invoice = True
            else:
                amc.invoice_count = 0
                amc.is_invoice = False

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string="Customer")
    status = fields.Selection([('draft', 'Draft'),
                               ('running', 'Running'),
                               ('expired', 'Expired')], string="Status", default='draft')
    user_id = fields.Many2one('res.users', string="Salesperson")
    line_ids = fields.One2many('amc.software', 'amc_id', string='Software')
    invoice_ids = fields.Many2many(
        'account.move', 'ethics_amc_invoice_rel', 'amc_id', 'invoice_id', string="Invoices")
    invoice_count = fields.Integer(
        compute="_compute_invoice", string='Invoice Count')
    store_name = fields.Char()
    store_code = fields.Char()
    area = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    country_id = fields.Many2one('res.country')
    contact_person = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    is_invoice = fields.Boolean()

    def _run_send_email_expiration(self):
        month_before = date.today() + relativedelta(months=+1)
        view = self.env.ref('ethics_amc.software_expiration', raise_if_not_found=False)
        if not view:
            _logger.warning('View "ethics_amc.software_expiration" was not found.')
            return False
        expire_software = self.env['amc.software'].sudo().search([
            ('expiery_date', '<=', month_before), ('expiery_date', '>=', date.today()), ('status', '=', 'running')])
        for software in expire_software:
            datediff = software.expiery_date - date.today()
            datediff = datediff.days
            week = datediff / 7
            create_values = {
                'body_html': view.render({'software': software, 'partner': software.amc_id.customer_id},
                                         engine='ir.qweb', minimal_qcontext=True),
                'email_from': software.amc_id.user_id.email or software.amc_id.customer_id.company_id.email,
                'recipient_ids': [(4, software.amc_id.customer_id.id)]
            }
            if software.expiery_date == month_before:
                create_values.update({'subject': _("%s Software Expire in 30 Days") % software.product_id.name})
                mail = self.env['mail.mail'].create(create_values)
                mail.send()
            elif (datediff <= 7 and datediff > 0):
                create_values.update(
                    {'subject': _("%s Expire in %s Days") % (software.product_id.name, datediff)})
                mail = self.env['mail.mail'].create(create_values)
                mail.send()
            elif week.is_integer() and week > 1:
                create_values.update(
                    {'subject': _("%s Expire in %s Week") % (software.product_id.name, int(week))})
                mail = self.env['mail.mail'].create(create_values)
                mail.send()
            else:
                create_values.update(
                    {'subject': _("%s Expire in %s Days") % (software.product_id.name, datediff)})
                mail = self.env['mail.mail'].create(create_values)
                mail.send()
        return True

    def go_to_invoice(self):
        ctx = dict(self._context)
        view_id = self.env.ref(
            'account.view_move_form')
        tree_view_id = self.env.ref(
            'account.view_invoice_tree')
        if self.invoice_ids:
            if len(self.invoice_ids.ids) > 1:
                return {
                    'name': _('Record'),
                    'view_type': 'form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'domain': "[('id', 'in',%s)]" % (self.invoice_ids.ids),
                    'context': ctx,
                    'views': [(tree_view_id.id, 'tree'), (view_id.id, 'form')],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'nodestroy': True
                }
            else:
                return {
                    'name': 'Record',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'res_id': self.invoice_ids.ids[0],
                    'view_id': view_id.id,
                }
        else:
            return {
                'name': 'Record',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_id': view_id.id,
            }

    def create_invoice(self):
        if self.invoice_ids:
            raise UserError(
                _("Invoice already created for this AMC."))
        line_data = []
        for line in self.line_ids:
            product = line.product_id
            account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            line_data.append((0, 0, {
                'name': product.name,
                'account_id': account.id,
                'price_unit': product.lst_price,
                'quantity': line.quantity,
                'product_uom_id': product.uom_id.id,
                'product_id': product.id,
                'tax_ids': [(6, 0, product.taxes_id.ids)],
            }))
        if line_data:
            value = {'partner_id': self.customer_id.id,
                     'move_type': 'out_invoice',
                     'invoice_line_ids': line_data,
                     'amc_id': self.id}
            invoice_id = self.env['account.move'].create(value)
            self.write({'invoice_ids': [(4, invoice_id.id)]})
            view_id = self.env.ref('account.view_move_form')
            return {
                'name': 'Record',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'res_id': invoice_id.id,
                'view_id': view_id.id,
            }

    def set_submit(self):
        self.ensure_one()
        self.write({'status': 'running'})

    def amc_expired(self):
        self.ensure_one()
        self.update({'status': 'expired'})

    def amc_renew(self):
        self.ensure_one()
        copy_amc = self.copy()
        copy_amc.invoice_ids = False
        copy_amc.invoice_count = 0
        copy_amc.status = 'draft'
        if self.line_ids:
            copy_lines = [line.with_context(copy_amc=copy_amc).copy().id for line in self.line_ids]
            copy_amc.update({'line_ids': [(6, 0, copy_lines)]})
        action = self.env.ref('ethics_amc.action_ethics_amc').read()[0]
        form_view = [(self.env.ref('ethics_amc.ethics_amc_form_view').id, 'form')]
        context = self._context.copy()
        action.update({'views': form_view, 'res_id': copy_amc.id, 'context': context})
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'ethics.amc') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('ethics.amc') or _('New')
        result = super(EthicsAmc, self).create(vals)
        return result


class EthicsPlan(models.Model):
    _name = "ethics.plan"
    _description = 'Plan Period in Month'
    _rec_name = 'name'

    name = fields.Char('Plan Name')
    months = fields.Integer('Months', required=True, copy=False)


class AmcSoftware(models.Model):
    _name = "amc.software"
    _description = 'Product'

    name = fields.Char(string='ID', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string="Product Name/Code")
    quantity = fields.Integer('Quantity', required=True)
    installation_date = fields.Date(string='Installation Date', required=True, index=True,
                                    default=fields.Date.context_today)
    plan_id = fields.Many2one('ethics.plan', string="Plan")
    expiery_date = fields.Date(string='Expiry Date', required=True, index=True, default=fields.Date.context_today)
    amc_id = fields.Many2one('ethics.amc', string="AMC")
    status = fields.Selection(related='amc_id.status', string='Status', readonly=True)
    partner_id = fields.Many2one(related='amc_id.customer_id', string='Customer')
    pre_expiry_date = fields.Date(stirng='Previous Expiry Date')
    renew_date = fields.Date(stirng='Renew Date')

    @api.onchange('plan_id', 'installation_date', 'pre_expiry_date')
    def onchange_plan(self):
        if self.plan_id and self.installation_date and not self.pre_expiry_date:
            plan = int(self.plan_id.months)
            expiery_date = self.installation_date + relativedelta(months=+plan)
            self.expiery_date = expiery_date
        elif self.plan_id and self.installation_date and self.pre_expiry_date:
            plan = int(self.plan_id.months)
            expiery_date = self.pre_expiry_date + relativedelta(months=+plan)
            self.expiery_date = expiery_date

    @api.model
    def create(self, vals):
        if vals.get('plan_id') and vals.get('installation_date'):
            plan = self.env['ethics.plan'].browse(vals.get('plan_id'))
            if plan and plan.months and not self._context.get('copy_amc'):
                if isinstance(vals.get('installation_date'), str):
                    date_time_obj = datetime.strptime(vals.get('installation_date'), '%Y-%m-%d')
                else:
                    date_time_obj = vals.get('installation_date')
                expiery_date = date_time_obj + relativedelta(months=+int(plan.months))
                vals['expiery_date'] = expiery_date
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'amc.software') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('amc.software') or _('New')
        if self._context.get('copy_amc') and vals.get('expiery_date'):
            if date.today() > vals.get('expiery_date'):
                renew_date = date.today()
            else:
                renew_date = vals.get('expiery_date')
            vals.update({'amc_id': self._context.get('copy_amc').id,
                         'pre_expiry_date': vals.get('expiery_date'), 'renew_date': renew_date})
            if vals.get('pre_expiry_date') and self.plan_id:
                plan = int(self.plan_id.months)
                expiery_date = vals.get('pre_expiry_date') + relativedelta(months=+plan)
                vals.update({'expiery_date': expiery_date})
        result = super(AmcSoftware, self).create(vals)
        return result

    def write(self, vals):
        res = super(AmcSoftware, self).write(vals)
        if vals.get('plan_id') or vals.get('installation_date'):
            for sw in self:
                plan = int(sw.plan_id.months)
                expiery_date = sw.installation_date + relativedelta(months=+plan)
                sw.expiery_date = expiery_date
        return res
