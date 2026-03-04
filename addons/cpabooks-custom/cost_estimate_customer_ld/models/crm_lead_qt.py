import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    order_line = fields.One2many('order.line', 'crm_id', string="Order Line")
    bypass_estimation=fields.Boolean(string="Bypass Estimation",default=0)
    qt_count = fields.Integer(compute='_compute_sale_qt', string="Number of Quotations")

    @api.depends('stage_id')
    def _compute_sale_qt(self):
        for rec in self:
            rec.qt_count = self.env['sale.order'].sudo().search_count([('crm_id', '=', rec.id)])

    def action_view_sale_qt(self):
        for rec in self:
            orders = self.env['sale.order'].sudo().search([('crm_id', '=', rec.id)])
            action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
            if len(orders) > 1:
                action['domain'] = [('id', 'in', orders.ids)]
            elif len(orders) == 1:
                form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = orders.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.onchange('company_id')
    def get_default_bypass_estimation(self):
        get_highest_lead = self.env['crm.lead'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if get_highest_lead:
            self.bypass_estimation = get_highest_lead.bypass_estimation

    def button_create_quotation(self):
        for rec in self:
            order_lines = []
            if not rec.partner_id:
                raise ValidationError("Customer required to create quotation")

            if rec.order_line:
                get_highest_quot = self.env['sale.order'].sudo().search(
                    [('company_id', '=', self.company_id.id)], limit=1)
                for line in rec.order_line:
                    val = (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'price_unit':line.price_unit,
                        'price_subtotal':line.price_subtotal
                    })
                    order_lines.append(val)

                order_id = self.env['sale.order'].create({
                    'partner_id': rec.partner_id.id,
                    'state': 'draft',
                    'date_order': datetime.datetime.now(),
                    'user_id': rec.user_id.id,
                    'company_id': rec.company_id.id or False,
                    'project_id':rec.project_id.id,
                    # 'order_line': order_lines,
                    'crm_id': rec.id,
                    'order_line': order_lines,
                })
            else:
                raise ValidationError("Order Line Required")


            return rec
