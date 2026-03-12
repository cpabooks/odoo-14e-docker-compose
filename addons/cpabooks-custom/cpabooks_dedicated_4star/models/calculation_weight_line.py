from odoo import api, models, fields, _
from odoo.exceptions import UserError


class CalculationWeightLine(models.Model):
    _name = 'calculation.weight.line'
    _description = 'Calculation by Weight Line'

    import_id = fields.Many2one('import.purchase.line', 'Import Line')
    order_id = fields.Many2one('purchase.order', 'Purchase')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency', related='order_id.currency_id', store=True)
    fr_currency_id = fields.Many2one('res.currency', string='Fr Currency')
    product_id = fields.Many2one('product.product', 'Product', compute='_get_product_id', inverse='_set_product_id',
                                 store=True)
    name = fields.Text('Item Description', compute='_get_product_description', readonly=False, store=True)
    weight_per_unit = fields.Float('Weight(gm)/Unit', digits=(16, 5))
    total_weight = fields.Float('Total Weight', digits=(16, 5))
    landed_cost_aed = fields.Float('Landed Cost AED', digits=(16, 5), compute='_compute_landed_cost_aed')
    landed_cost_per_unit = fields.Float('LC / Unit', digits=(16, 5), compute='_compute_landed_cost_per_unit')
    material_cost_per_unit = fields.Float('Material Cost', digits=(16, 5), compute='_compute_material_cost_per_unit')
    final_unit_price = fields.Float('Final Unit Price AED', digits=(16, 5), compute='_compute_final_unit_price')

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
        for rec in self:
            if rec.product_id:
                rec.name = f"{rec.product_id.name}\n{rec.product_id.prod_description or ''}"
            else:
                rec.name = False  # ✅ Avoid assigning None

    @api.depends('weight_per_unit')
    def _compute_total_weight(self):
        """Calculate Total Weight"""
        for rec in self:
            try:
                qty = rec.import_id.product_qty if rec.import_id else 0.0
                rec.total_weight = rec.weight_per_unit * qty
            except Exception as e:
                print(e)
                rec.total_weight = 0.0

    def _get_total_amount(self, order_id=False):
        """Get Sum of total amount from Landed Cost Input Line"""
        if not order_id:
            return 0.0
        landed_cost_line = self.env['landed.cost.line'].search([
            ('company_id', '=', self.env.company.id),
            ('order_id', '=', order_id.id)
        ])
        return sum(landed_cost_line.mapped('amount_in_aed'))

    def _get_total_qty(self, order_id=False):
        """Calculate total weight from Calculation by weight line"""
        if not order_id:
            return 0.0
        calculation_weight_line_ids = self.env['calculation.weight.line'].search([
            ('company_id', '=', self.env.company.id),
            ('order_id', '=', order_id.id)
        ])
        return sum(calculation_weight_line_ids.mapped('total_weight'))

    @api.depends('total_weight', 'order_id')
    def _compute_landed_cost_aed(self):
        """Calculate Landed Cost in AED"""
        for rec in self:
            try:
                total_amount = rec._get_total_amount(rec.order_id) if rec.order_id else 0.0
                total_weight = rec._get_total_qty(rec.order_id) if rec.order_id else 0.0
                landed_cost = (total_amount / total_weight) * rec.total_weight if rec.total_weight else 0.0
                rec.landed_cost_aed = landed_cost
            except Exception as e:
                print(e)
                rec.landed_cost_aed = 0.0

    @api.depends('import_id', 'landed_cost_aed')
    def _compute_final_unit_price(self):
        """Calculate final price in AED"""
        for rec in self:
            try:
                amount = rec.import_id.amount_in_aed if rec.import_id else 0.0
                qty = rec.import_id.product_qty if rec.import_id else 0.0
                rec.final_unit_price = (rec.landed_cost_aed + amount) / qty
            except Exception as e:
                print(e)
                rec.final_unit_price = 0.0

    def _get_import_line_with_qty(self):
        import_line = self.env['import.purchase.line'].search([
            ('id', '=', self.import_id.id)
        ], limit=1)
        if not import_line:
            raise UserError(_("No Import purchase line is given for this product"))
        if import_line.product_qty <= 0:
            raise UserError(_("Invalid product quantity in import line!"))
        return import_line

    @api.onchange('weight_per_unit')
    def calculate_total_weight(self):
        """Cal calculate total weight if weight per unit is given"""
        import_line = self._get_import_line_with_qty()
        if self.weight_per_unit and import_line:
            total_weight = self.weight_per_unit * import_line.product_qty
            self.total_weight = total_weight
        else:
            self.total_weight = 0.0

    @api.onchange('total_weight')
    def calculate_weight_per_unit(self):
        """Cal calculate weight per unit if total weight is given"""
        import_line = self._get_import_line_with_qty()
        if self.total_weight and import_line:
            weight_per_unit = self.total_weight / import_line.product_qty
            self.weight_per_unit = weight_per_unit
        else:
            self.weight_per_unit = 0.0

    @api.depends('landed_cost_aed')
    def _compute_landed_cost_per_unit(self):
        for rec in self:
            import_line = rec._get_import_line_with_qty()
            rec.landed_cost_per_unit = rec.landed_cost_aed / import_line.product_qty if import_line and rec.landed_cost_aed else 0.0

    def _compute_material_cost_per_unit(self):
        for rec in self:
            import_line = rec._get_import_line_with_qty()
            rec.material_cost_per_unit = import_line.amount_in_aed / import_line.product_qty if import_line else 0.0
