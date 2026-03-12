from odoo import models, fields, api, _
from odoo.tools import float_compare


class stockPicking(models.Model):
    _inherit = 'stock.picking'

    # @api.depends('move_type', 'immediate_transfer', 'move_lines.state', 'move_lines.picking_id')
    # def _compute_state(self):
    #     ''' State of a picking depends on the state of its related stock.move
    #     - Draft: only used for "planned pickings"
    #     - Waiting: if the picking is not ready to be sent so if
    #       - (a) no quantity could be reserved at all or if
    #       - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
    #     - Waiting another move: if the picking is waiting for another move
    #     - Ready: if the picking is ready to be sent so if:
    #       - (a) all quantities are reserved or if
    #       - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
    #     - Done: if the picking is done.
    #     - Cancelled: if the picking is cancelled
    #     '''
    #     super(stockPicking, self)._compute_state()
    #     for rec in self:
    #         rec.state='confirmed'

    def action_set_quantities_to_reservation(self):
        if self.picking_type_code=="outgoing":
            for move in self.move_ids_without_package:
                if  move.has_tracking == 'none' :
                    if not move.move_line_ids:
                        move.move_line_ids+=self.env['stock.move.line'].sudo().create({
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_uom.id,
                            # 'product_uom_qty': line.product_uom_qty - line.delivered_qty,
                            'location_id': move.warehouse_id.lot_stock_id.id,
                            'location_dest_id': 5,
                            # 'state': 'assigned',
                            'product_description': move.name,
                            'move_id':move.id,
                            'picking_id':self.id
                        })

            self.move_lines._set_quantities_to_reservation_for_sale()
        #     for line in self.move_ids_without_package.move_line_ids:
        #         rounding = line.product_id.uom_id.rounding
        #         quants = self.env['stock.quant']._gather(line.product_id, line.location_id, lot_id=False, package_id=False, owner_id=False,
        #                               strict=True)
        #         available_quantity = sum(quants.mapped('reserved_quantity'))
        #         if float_compare(abs(line.product_qty), available_quantity, precision_rounding=rounding) > 0:
        #             line.write({
        #                 'product_uom_qty':0,
        #                 'qty_done':line.product_uom_qty
        #             })

        else:
            self.move_lines._set_quantities_to_reservation()

