from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        move_vales=super(StockPicking, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        move_vales['description_picking']=self.env['sale.order.line'].sudo().search([('id','=',int(values['sale_line_id']))]).name
        return move_vales