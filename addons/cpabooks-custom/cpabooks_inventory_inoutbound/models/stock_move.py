from odoo import fields, models, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    barcode = fields.Char(related='product_id.barcode', store=True)
    container_no = fields.Char(string='Container No')
    short_excess_qty = fields.Float(string='Qty (Short/Excess)', digits='Product Unit of Measure',  default=0.0)
    container_status = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('clear', 'Cleared'),
    ], string='Container Status', required=True, copy=False, tracking=True,
        default='pending')


    # @api.depends("product_uom_qty", "quantity_done")
    # def _get_short_excess_qty(self):
    #     for rec in self:
    #         diff_qty = rec.quantity_done - rec.product_uom_qty
    #         rec.short_excess_qty = diff_qty if diff_qty > 0 else 0

    # @api.depends('move_line_ids.product_qty')
    # def _compute_reserved_availability(self):
    #     if not self._origin:
    #         self.reserved_availability = 0
    #     else:
    #         for rec in self:
    #             rec.reserved_availability = rec.product_uom_qty

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    production_date = fields.Date(string='Production Date', copy=False)
    container_no = fields.Char(string='Container No')
    stock_qty = fields.Float(string='Stock Quantity', store=True) #, compute='_compute_product_stock_qty'
    is_stock_qty = fields.Boolean('Is Stock', default=lambda self: self.get_default_is_stock_qty())


    def get_default_is_stock_qty(self):
        # get_last_pick = self.env['stock.move'].search([('id','=', self.picking_id.id)],limit=1)
        print(self.picking_id.id)


    @api.onchange('lot_id.product_qty')
    def get_default_domain(self):
        return {'domain':{'lot_id': [('product_qty','>',0.00)]}}

    @api.onchange('stock_qty')
    def get_is_stock_qty(self):
        for rec in self:
            if rec.stock_qty > 0.00:
                rec.is_stock_qty = True
            else:
                rec.is_stock_qty = True

    def _assign_production_lot(self, lot):
        super()._assign_production_lot(lot)
        self.lot_id.update({'production_date': self.production_date,'expiration_date':self.expiration_date, 'ref': self.container_no})


    # @api.onchange('lot_id')
    # def _compute_product_stock_qty(self):
    #     for rec in self:
    #         if rec.lot_id:
    #             rec.stock_qty = rec.lot_id.product_qty
    #         else:
    #             rec.stock_qty = 0.00

        # self.stock_qty = 0
    @api.onchange('lot_id')
    @api.depends('production_date')
    def _onchange_lot_id(self):
        self.production_date = self.lot_id.production_date
        self.stock_qty = self.lot_id.product_qty
        if self.move_id.picking_code=='outgoing':
            self.expiration_date = self.lot_id.expiration_date
        if self.lot_id.product_qty <= 0:
            self.container_no = False
        else:
            self.container_no = self.lot_id.ref


