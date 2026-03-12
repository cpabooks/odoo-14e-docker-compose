import datetime

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class SaleOrderInheritance(models.Model):
    _inherit = 'sale.order'

    def action_create_rfq(self, default=None):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if default is None:
            default = {}
        if 'order_line' not in default:
            line_arr=[]
            for line in self.order_line.filtered(lambda l: not l.is_downpayment):
                vals=(0,0,{
                    'product_template_id':self.env['product.template'].search([('id','=',line.product_id.product_tmpl_id.id)]).id,
                    'product_id':line.product_id.id,
                    'name':line.product_id.name,
                    'product_qty':line.product_uom_qty,
                    'product_uom':line.product_id.uom_id.id,
                    'date_planned':datetime.datetime.now(),
                    'price_unit':line.product_id.standard_price
                })
                line_arr.append(vals)
            # default['order_line'] = [(0, 0, line.copy_data()[0]) for line in
            #                          self.order_line.filtered(lambda l: not l.is_downpayment)]
            default['order_line'] = line_arr
            # default['revise'] = True
        # data = super(SaleOrderInheritance, self).copy(default)
        default['partner_id']=self.partner_id.id
        data=self.env['purchase.order'].sudo().create(default)
        action['context'] = dict(self.env.context)
        action['context']['form_view_initial_mode'] = 'edit'
        action['context']['view_no_maturity'] = False
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = data.id

        return action
        # return {
        #     # 'name': self.display_name,
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'sale.order',
        #     'res_id': data.id,
        # }