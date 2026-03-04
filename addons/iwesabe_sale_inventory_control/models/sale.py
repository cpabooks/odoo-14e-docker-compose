# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	def action_confirm(self):
		for line in self.order_line.filtered(lambda x:x.product_id.type == 'product' and not x.product_id.allow_negative_stock):
			stock_quant_id = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','=',self.warehouse_id.lot_stock_id.id)],limit=1)
			if not stock_quant_id:
				raise ValidationError(_("Stock location not found for %s"%(line.product_id.display_name)))
			available_quantity = line.product_id.uom_id._compute_quantity(stock_quant_id.available_quantity, line.product_uom)
			if line.product_uom_qty > available_quantity:
				raise ValidationError(_("%s's Location/Warehouse Has Product With Available QTY %s %s"%(line.product_id.display_name,stock_quant_id.available_quantity,stock_quant_id.product_uom_id.name)))
		result = super().action_confirm()
		if self.picking_ids:
			for picking in self.picking_ids:
				for move_line in picking.move_ids_without_package.filtered(lambda x:x.product_id.allow_negative_stock):
					move_line.quantity_done = move_line.product_uom_qty
		return result