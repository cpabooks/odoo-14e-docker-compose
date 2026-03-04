from odoo import models, fields, api, _


class stockMove(models.Model):
    _inherit = 'stock.move'



    def _set_quantities_to_reservation(self):
        for move in self:
            if move.state not in ('partially_available', 'assigned'):
                continue
            for move_line in move.move_line_ids:
                if move.has_tracking != 'none' and not (move_line.lot_id or move_line.lot_name):
                    continue
                move_line.qty_done = move_line.product_uom_qty

    def _set_quantities_to_reservation_for_sale(self):
        for move in self:
            move.state='assigned'
            move.picking_id.state='assigned'
            for move_line in move.move_line_ids:
                if move.has_tracking != 'none' and not (move_line.lot_id or move_line.lot_name):
                    continue
                move_line.qty_done = move.product_uom_qty

