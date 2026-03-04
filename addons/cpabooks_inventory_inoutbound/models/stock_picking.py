from odoo import fields, models, api


class VehicleNo(models.Model):
    _name = 'vehicle.no'
    _description = 'Vehicle No'
    _rec_name = 'name'

    name = fields.Char(string="Vehicle No")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    lot_no_id = fields.Many2one('stock.production.lot', 'Lot No.', related='move_line_ids.lot_id')
    lot_no_ids = fields.One2many('stock.move.line', 'picking_id', string='Lots')
    lot_no_qty_done = fields.Char('Done Qty', compute='_compute_lot_no_qty_done')


    driver_name = fields.Many2one('res.partner', tracking=True,
        check_company=True,
        string='Driver Name')
    vehicle_no = fields.Many2one('vehicle.no', string="Vehicle No")
    container_status = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('clear', 'Cleared'),
        ('cancel', 'Cancelled'),
    ], string='Container Status', required=True, readonly=True, copy=False, tracking=True,
        default='pending')
    partner_id = fields.Many2one('res.partner', string="Customer Name", required=True,
                                 default=lambda self: self.env.user.partner_id.id)
    warehouse_ref = fields.Char(string="Warehouse Ref")
    origin = fields.Char(string="BL No")
    declaration_no = fields.Char(string="Declaration No")
    container_no = fields.Char(string="Container No")
    invoice_no = fields.Char(string="Invoice No")

    @api.depends('move_lines.state', 'move_lines.date', 'move_type')
    def _compute_scheduled_date(self):
        return

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        self.write({'date_done': self.scheduled_date, 'priority': '0'})
        return res


    # @api.model
    # def default_get(self, fields_list):
    #     defaults = super(StockPicking, self).default_get(fields_list)
    #
    #     # Assuming you want to set the default lot number from the first stock move record
    #     stock_move = self.env['stock.move'].search([], limit=1)
    #     if stock_move:
    #         defaults['lot_no_id'] = stock_move.lot_id.id
    #
    #     return defaults

    def _compute_lot_no_qty_done(self):
        for picking in self:
            total_qty_done = sum(picking.lot_no_ids.mapped('qty_done'))
            picking.lot_no_qty_done = total_qty_done

    def set_draft(self):
        self._cr.execute(
            """UPDATE stock_picking SET state='draft' WHERE id='%s'""" % self.id)
        self._cr.commit()

        self._cr.execute(
            """UPDATE stock_move SET state='draft' WHERE picking_id='%s'""" % self.id)
        self._cr.commit()

        self._cr.execute(
            """UPDATE stock_move_line SET state='draft' WHERE picking_id='%s'""" % self.id)
        self._cr.commit()


    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        super(StockPicking, self).onchange_picking_type()

        if self.partner_id.allow_location_ids:
            if self.picking_type_id.code == 'outgoing':
                self.location_id = self.partner_id.allow_location_ids[0].id
            elif self.picking_type_id.code == 'incoming':
                self.location_dest_id = self.partner_id.allow_location_ids[0].id

    # @api.model
    # def create(self, vals):
    #     res = super(StockPicking, self).create(vals)
    #     for move in res.move_lines:
    #         move.update({'container_no': vals['container_no']})
    #     return res

    def button_validate(self):
        self.container_status = 'clear'
        for move in self.move_lines:
            #diff_qty = move.quantity_done - move.product_uom_qty
            # rec.short_excess_qty = diff_qty if diff_qty > 0 else 0
            #move.update({'container_status': 'clear', 'short_excess_qty': diff_qty if diff_qty > 0 else 0})
            move.update({'container_status': 'clear'})
        self.state = 'done'
        super(StockPicking, self).button_validate()
    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        for rec in res.move_lines:
            rec.write({'reserved_availability': rec.product_uom_qty})
        return res



