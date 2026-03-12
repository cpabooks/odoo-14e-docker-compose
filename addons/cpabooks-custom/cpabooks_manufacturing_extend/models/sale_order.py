import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id','product_uom_qty')
    def check_stock_and_bom(self):
        for rec in self:
            get_total_qty = sum(
                self.env['stock.quant'].sudo().search([('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id),
                                                       ('company_id', '=', self.env.company.id),
                                                       ('product_id', '=', rec.product_id.id)]).mapped('quantity'))
            get_reserved_qty = sum(
                self.env['stock.quant'].sudo().search([('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id),
                                                       ('company_id', '=', self.env.company.id),
                                                       ('product_id', '=', rec.product_id.id)]).mapped(
                    'reserved_quantity'))
            if rec.product_id.tracking=='serial':

                if get_total_qty-get_reserved_qty<=0:
                    if not self.env['mrp.bom'].sudo().search([('product_id','=',rec.product_id.id)],limit=1):
                        raise ValidationError(_(f"{rec.product_id.name} Product has no available quantity, Also no recipe/BoM found for production"))
            if rec.product_id.tracking == 'none':
                if sum(self.env['stock.quant'].sudo().search([('location_id','=',rec.order_id.warehouse_id.lot_stock_id.id),
                                                              ('company_id','=',self.env.company.id),('product_id','=',rec.product_id.id),('reserved_quantity','!=',1)]).mapped('quantity'))<=0:
                    if not self.env['mrp.bom'].sudo().search([('product_id','=',rec.product_id.id)],limit=1):
                        raise ValidationError(_(f"{rec.product_id.name} Product has no available quantity, Also no recipe/BoM found for production"))
