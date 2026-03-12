from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def reserve_qty(self):
        for rec in self:
            for line in rec.move_line_ids_without_package:
                if line.product_id.tracking=='serial':
                    get_stock_line=self.env['stock.quant'].sudo().search([('product_id','=',line.product_id.id),
                                                                          ('location_id','=',rec.location_id.id),
                                                                          ('company_id','=',rec.company_id.id),('lot_id','=',line.lot_id.id)],limit=1)
                    if not get_stock_line:
                        raise ValidationError(_("Lot:"+line.lot_id.name+" does not exists in your stock"))
                    if get_stock_line and get_stock_line.quantity>0 and get_stock_line.reserved_quantity==0:
                        get_stock_line.reserved_quantity=1


                if line.product_id.tracking=='none':
                    get_stock_line=self.env['stock.quant'].sudo().search([('product_id','=',line.product_id.id),
                                                                          ('location_id','=',rec.location_id.id),
                                                                          ('company_id','=',rec.company_id.id)],limit=1)
                    if not get_stock_line:
                        raise ValidationError(_("No Record Found for Product:\n" + line.product_id.name))
                    if get_stock_line and get_stock_line.quantity>0 and get_stock_line.reserved_quantity<line.product_uom_qty and line.product_uom_qty+get_stock_line.reserved_quantity<=get_stock_line.quantity:
                        get_stock_line.reserved_quantity+=line.product_uom_qty




        return True