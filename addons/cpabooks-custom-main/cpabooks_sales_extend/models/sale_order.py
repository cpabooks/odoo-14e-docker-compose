from datetime import datetime
from decimal import Decimal

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.tools import get_lang


class SaleOrderInheritance(models.Model):
    _inherit = 'sale.order'

    sale_history=fields.One2many('sale.history.data','sale_order_id')
    stock_history=fields.One2many('stock.history.data','sale_order_id')
    product_ids=fields.Many2one('product.product')

    @api.onchange('order_line')
    def set_val(self):
        for order in self:
            if order.order_line:
                last_line=order.order_line[-1]
                print(last_line.product_id.name)
                if last_line.product_id and order.partner_id:
                    order.sale_history=[(5,0,0)]
                    order.stock_history=[(5,0,0)]
                    query="""select so.date_order::date as date,so.id as doc_no,sol.product_uom_qty as qty,sol.qty_delivered as delivery_qty,
                                sol.price_unit as rate from sale_order so
                            left join sale_order_line sol on sol.order_id=so.id
                            where so.state in {} and sol.product_id={} and
                            so.partner_id={} order by date_order::date desc""".format(('sale','done'),last_line.product_id.id,order.partner_id.id)
                    self._cr.execute(query=query)
                    get_sale_history=self._cr.fetchall()
                    sale_history=[]
                    for sh in get_sale_history:
                        if sh[3]>0:
                            vals=(0,0,{
                                'date':sh[0],
                                'doc_no':sh[1],
                                'quantity':sh[2],
                                'delivered_qty':sh[3],
                                'rate':sh[4],
                            })
                            sale_history.append(vals)
                    order.sale_history=sale_history

                    query="""select sl.id,sl.name,sum(sq.quantity) from stock_quant sq 
                            left join stock_location sl on sl.id=sq.location_id
                            where sq.product_id={} and sl.usage='{}' group by sl.id,sl.name""".format(last_line.product_id.id,'internal')
                    self._cr.execute(query=query)
                    get_stock_history = self._cr.fetchall()

                    stock_history = []
                    for sh in get_stock_history:
                        vals = (0, 0, {
                            'stock_location': sh[0],
                            'quantity': sh[2],
                        })
                        stock_history.append(vals)
                    order.stock_history = stock_history






class SaleHistoryData(models.TransientModel):
    _name = "sale.history.data"

    sale_order_id=fields.Many2one('sale.order')
    date=fields.Date(string='Date')
    doc_no=fields.Many2one('sale.order',string="Document No")
    quantity=fields.Float(string="Quantity")
    delivered_qty=fields.Float(string="Delivered Quantity")
    rate=fields.Float(string="Rate")

class StockHistoryData(models.TransientModel):
    _name = 'stock.history.data'

    sale_order_id = fields.Many2one('sale.order')
    stock_location=fields.Many2one('stock.location',string="Stock Location")
    quantity=fields.Float(string="Quantity")