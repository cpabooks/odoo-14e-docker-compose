from odoo import api, models, fields, _
from odoo.exceptions import UserError


class CalculationVolumeLine(models.Model):
    _name = 'calculation.volume.line'
    _description = 'Calculation by volume line'

    import_id = fields.Many2one('import.purchase.line', 'Import Line')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency', related='order_id.currency_id', store=True)
    order_id = fields.Many2one('purchase.order', 'Purchase')
    fr_currency_id = fields.Many2one('res.currency', string='Fr Currency')
    product_id = fields.Many2one('product.product', 'Product', compute='_get_product_id', inverse='_set_product_id')
    name = fields.Text('Item Description', compute='_get_product_description', readonly=False)
    volume_per_unit = fields.Float('Volume/Unit', digits=(16, 5), default=0.0)
    total_volume = fields.Float('Total Volume(Cbm)',digits=(16, 5), default=0.0)
    landed_cost_aed = fields.Float('Landed Cost AED',digits=(16, 5),
                                      compute='_compute_landed_cost_aed')
    landed_cost_per_unit = fields.Float('LC / Unit',digits=(16, 5),
                                           compute='_compute_landed_cost_per_unit')
    material_cost_per_unit = fields.Float('Material Cost',digits=(16, 5),
                                             compute='_compute_material_cost_per_unit')
    price_unit_final_aed = fields.Float('Final Unit Price(AED)',digits=(16, 5),
                                           compute='_compute_final_unit_price_aed')
    import_purchase_total = fields.Float('Import Total', compute='_compute_import_total', digits=(16, 5))
    amount_total = fields.Float('Total', (16, 5), compute='_compute_amount_total')
    product_qty = fields.Float('Qty', compute='_compute_product_qty')

    @api.depends('import_id')
    def _compute_product_qty(self):
        for rec in self:
            if rec.import_id:
                rec.product_qty = rec.import_id.product_qty if rec.import_id.product_qty else 0.0

    @api.depends('import_purchase_total', 'landed_cost_aed')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.import_purchase_total + rec.landed_cost_aed

    @api.depends('import_id')
    def _compute_import_total(self):
        for rec in self:
            if rec.import_id:
                rec.import_purchase_total = rec.import_id.amount_in_aed if rec.import_id.amount_in_aed else 0.0

    def _get_import_line_with_qty(self):
        """Check Validation of import_id and quantity"""
        if not self.import_id:
            raise UserError(_("No Import purchase line is given for this product"))
        elif self.import_id.product_qty <= 0:
            raise UserError(_("Invalid product quantity in import line!"))
        return self.import_id

    @api.onchange('volume_per_unit')
    def calculate_total_volume(self):
        """Calculate total volume based on volume per unit and import_line.quantity"""
        import_line = self._get_import_line_with_qty()
        if import_line and self.volume_per_unit:
            self.total_volume = import_line.product_qty * self.volume_per_unit
        else:
            self.total_volume = 0.0

    @api.onchange('total_volume')
    def calculate_volume_per_unit(self):
        import_line = self._get_import_line_with_qty()
        if import_line and self.total_volume:
            self.volume_per_unit = self.total_volume / import_line.product_qty
        else:
            self.volume_per_unit = 0.0

    @api.depends('import_id.product_id')  # ✅ Added dependency
    def _get_product_id(self):
        for rec in self:
            rec.product_id = rec.import_id.product_id if rec.import_id else False  # ✅ Assign Many2one field correctly

    def _set_product_id(self):
        for rec in self:
            if rec.import_id:
                rec.import_id.product_id = rec.product_id  # ✅ Assigning correctly
            else:
                rec.import_id.product_id = False  # ✅ Using False instead of None

    @api.depends('product_id')
    def _get_product_description(self):
        """Get product Description"""
        for rec in self:
            if rec.product_id:
                rec.name = f"{rec.product_id.name}\n{rec.product_id.prod_description or ''}"
            else:
                rec.name = False

    def _calculate_landed_input_cost(self, order_id):
        """Calculate landed input cost for the given order_id"""
        if not order_id:
            return 1.0
        landed_line_ids = self.env['landed.cost.line'].search([
            ('company_id', '=', self.env.company.id),
            ('order_id', '=', order_id)
        ])
        return sum(landed_line_ids.mapped('amount_in_aed'))  # ✅ Optimized sum calculation

    def _calculate_total_volume(self, order_id):
        """Calculate total volume from volume line"""
        if not order_id:
            return 1.0
        volume_line_ids = self.env['calculation.volume.line'].search([
            ('order_id', '=', order_id),
            ('company_id', '=', self.env.company.id)
        ])
        return sum(volume_line_ids.mapped('total_volume'))

    @api.depends('import_id', 'product_id')
    def _compute_landed_cost_aed(self):
        """Compute landed cost AED"""
        for rec in self:
            try:
                total_landed_cost_aed = rec._calculate_landed_input_cost(rec.order_id.id) if rec.order_id else 1.0
                # Total volume for all lines.
                total_volume = rec._calculate_total_volume(rec.order_id.id) if rec.order_id else 1.0

                rec.landed_cost_aed = (total_landed_cost_aed / total_volume) * rec.total_volume
            except Exception as e:
                print(e)
                rec.landed_cost_aed = 0.0

    @api.depends('landed_cost_aed', 'import_id')
    def _compute_final_unit_price_aed(self):
        """Calculate final price in aed"""
        for rec in self:
            try:
                # price in aed
                total_amount = rec.import_id.amount_in_aed if rec.import_id else 0.0  # get total amount from import_id
                qty = rec.import_id.product_qty if rec.import_id else 0.0
                final_unit_price = (rec.landed_cost_aed + total_amount) / qty
                rec.price_unit_final_aed = final_unit_price
            except Exception as e:
                print(e)
                rec.price_unit_final_aed = 0.0

    @api.depends('landed_cost_aed')
    def _compute_landed_cost_per_unit(self):
        for rec in self:
            if rec.landed_cost_aed:
                import_line = rec._get_import_line_with_qty()
                rec.landed_cost_per_unit = rec.landed_cost_aed / import_line.product_qty
            else:
                rec.landed_cost_per_unit = 0.0

    @api.depends('import_id')
    def _compute_material_cost_per_unit(self):
        for rec in self:
            import_line = rec._get_import_line_with_qty()
            if import_line:
                rec.material_cost_per_unit = import_line.amount_in_aed / import_line.product_qty
            else:
                rec.material_cost_per_unit = 0.0
