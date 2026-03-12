from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools import float_is_zero, float_round


class MrpProductionInherit(models.Model):
    _inherit = "mrp.production"


    bom_reference = fields.Char(string='BOM Reference', related='bom_ref.name')

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('id', 'in', allowed_product_ids)]",
        readonly=True, required=False, check_company=True,
        states={'draft': [('readonly', False)]})

    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits='Product Unit of Measure',
        readonly=True, required=False, tracking=True,
        states={'draft': [('readonly', False)]})

    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        readonly=True, required=False,
        states={'draft': [('readonly', False)]}, domain="[('category_id', '=', product_uom_category_id)]")

    final_product_ids=fields.One2many('mrp.final.product','production_id')

    bom_ref=fields.Many2one("mrp.bom",string="BoM", context={'is_for_mo': True})

    # @api.model
    # def create(self,val_list):
    #     rec=super(MrpProductionInherit, self).create(val_list)
    #     fp_vals = []
    #     location_dest_id = rec._get_default_location_dest_id()
    #     for bom_line in rec.final_product_ids:
    #         fp_vals.append(
    #             rec._get_move_finished_values_multi(bom_line.final_product_id.id, bom_line.quantity,
    #                                                   bom_line.final_product_id.uom_id.id, location_dest_id))

    @api.onchange('bom_ref')
    def set_data(self):
        for rec in self:
            rec.move_raw_ids=[(5,0,0)]
            rec.final_product_ids=[(5,0,0)]
            rec.move_finished_ids=[(5,0,0)]
            try:
                location_dest_id = rec._get_default_location_dest_id()
                rec.bom_reference=rec.bom_ref.name
                val_list=[]
                for line in rec.bom_ref.bom_line_ids:
                    vals=(0,0,{
                        'bom_product_id':line.bom_product_id.id,
                        'product_id':line.product_id.id,
                        'product_uom_qty':line.product_qty,
                        'name':line.product_id.name,
                        'product_uom':line.product_id.uom_id.id,
                        'location_dest_id': line.bom_product_id.with_company(
                            self.company_id).property_stock_production.id,
                        'mo_raw_actual_qty': line.product_qty
                    })
                    val_list.append(vals)
                rec.move_raw_ids=val_list
                f_val_list=[]
                for f_line in rec.bom_ref.final_product_ids:
                    vals=(0,0,{
                        'final_product_id':f_line.final_product_id.id,
                        'quantity':f_line.quantity,
                        'actual_quantity': f_line.quantity
                    })
                    f_val_list.append(vals)
                rec.final_product_ids=f_val_list
                fp_vals = []
                for bom_line in rec.bom_ref.final_product_ids:
                    fp_vals.append((0,0,
                        rec._get_move_finished_values_multi(bom_line.final_product_id.id, bom_line.quantity,
                                                            bom_line.final_product_id.uom_id.id, location_dest_id)))
                rec.move_finished_ids=fp_vals
            except AccessError as e:
                print("****")

    # @api.model
    # def action_create_mrp_immediate_production(self):
    #     query="""select * from mrp_production_production_rel where mrp_immediate_production_id not in (select id from mrp_immediate_production)"""
    #     self._cr.execute(query=query)
    #     get_data = self._cr.fetchall()
    #     immediate_production_id = [data[0] for data in get_data]
    #     if immediate_production_id:
    #         query="""delete from mrp_production_production_rel where mrp_immediate_production_id in {}""".format(str(tuple(immediate_production_id)).replace(',)',')'))
    #         self._cr.execute(query=query)
    #         self._cr.commit()

    @api.onchange('final_product_ids')
    def set_mo_quantity(self):
        for rec in self:
            for fp_line in rec.final_product_ids:
                for line in rec.move_raw_ids:
                    if line.bom_product_id.id==fp_line.final_product_id.id:
                        line.product_uom_qty=line.mo_raw_actual_qty*fp_line.quantity



    def _get_move_finished_values_multi(self, product_id, product_uom_qty, product_uom,location_dest_id, operation_id=False,
                                  byproduct_id=False):
        group_orders = self.procurement_group_id.mrp_production_ids
        move_dest_ids = self.move_dest_ids
        if len(group_orders) > 1:
            move_dest_ids |= group_orders[0].move_finished_ids.filtered(
                lambda m: m.product_id == self.product_id).move_dest_ids
        date_planned_finished = self.date_planned_start + relativedelta(days=self.product_id.produce_delay)
        date_planned_finished = date_planned_finished + relativedelta(days=self.company_id.manufacturing_lead)
        if date_planned_finished == self.date_planned_start:
            date_planned_finished = date_planned_finished + relativedelta(hours=1)
        return {
            'product_id': product_id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom,
            'operation_id': operation_id,
            'byproduct_id': byproduct_id,
            'name': self.name,
            'date': date_planned_finished,
            'date_deadline': self.date_deadline,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.env['product.product'].search([('id','=',product_id)]).with_company(self.company_id).property_stock_production.id,
            'location_dest_id': location_dest_id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.env['stock.location'].search([('id','=',location_dest_id)]).get_warehouse().id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
            'move_dest_ids': [(4, x.id) for x in move_dest_ids],

        }

    def action_confirm(self):
        self._check_company()
        for production in self:
            for fp_line in production.final_product_ids:
                get_fp = self.env['stock.move'].search(
                    [('production_id', '=', production.id), ('product_id', '=', fp_line.final_product_id.id)])
                get_fp.write({
                    'product_uom_qty':fp_line.quantity,
                })
            if production.bom_id:
                production.consumption = production.bom_id.consumption
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            # In case of Serial number tracking, force the UoM to the UoM of product
            if production.product_tracking == 'serial' and production.product_uom_id != production.product_id.uom_id:
                production.write({
                    'product_qty': production.product_uom_id._compute_quantity(production.product_qty, production.product_id.uom_id),
                    'product_uom_id': production.product_id.uom_id
                })
            # for move_finish in production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id):
            # for product in
            # for move_finish in production.move_finished_ids:
            #     move_finish.write({
            #         # 'product_uom_qty': move_finish.product_uom._compute_quantity(move_finish.product_uom_qty, move_finish.product_uom),
            #         'product_uom_qty': move_finish.product_uom_qty,
            #         'product_uom': move_finish.product_uom
            #     })
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
            # production.workorder_ids._action_confirm()
            # run scheduler for moves forecasted to not have enough in stock
            # production.move_raw_ids._trigger_scheduler()
        return True

    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids', 'workorder_ids.state', 'product_qty', 'qty_producing')
    def _compute_state(self):
        """ Compute the production state. It use the same process than stock
        picking. It exists 3 extra steps for production:
        - progress: At least one item is produced or consumed.
        - to_close: The quantity produced is greater than the quantity to
        produce and all work orders has been finished.
        """
        # TODO: duplicated code with stock_picking.py
        for production in self:
            for fp in production.final_product_ids:
                if not production.move_raw_ids:
                    production.state = 'draft'
                elif all(move.state == 'draft' for move in production.move_raw_ids):
                    production.state = 'draft'
                elif all(move.state == 'cancel' for move in production.move_raw_ids):
                    production.state = 'cancel'
                elif all(move.state in ('cancel', 'done') for move in production.move_raw_ids):
                    production.state = 'done'
                elif production.qty_producing >= production.product_qty:
                    production.state = 'to_close'
                elif any(wo_state in ('progress', 'done') for wo_state in production.workorder_ids.mapped('state')):
                    production.state = 'progress'
                elif not float_is_zero(fp.quantity, precision_rounding=fp.final_product_id.uom_id.rounding):
                    production.state = 'progress'
                elif any(not float_is_zero(move.quantity_done,
                                           precision_rounding=move.product_uom.rounding or move.product_id.uom_id.rounding)
                         for move in production.move_raw_ids):
                    production.state = 'progress'
                else:
                    production.state = 'confirmed'

                # Compute reservation state
                # State where the reservation does not matter.
                production.reservation_state = False
                # Compute reservation state according to its component's moves.
                if production.state not in ('draft', 'done', 'cancel'):
                    relevant_move_state = production.move_raw_ids._get_relevant_state_among_moves()
                    if relevant_move_state == 'partially_available':
                        if production.bom_id.operation_ids and production.bom_id.ready_to_produce == 'asap':
                            production.reservation_state = production._get_ready_to_produce_state()
                        else:
                            production.reservation_state = 'confirmed'
                    elif relevant_move_state != 'draft':
                        production.reservation_state = relevant_move_state

    def _pre_button_mark_done(self):
        productions_to_immediate = self._check_immediate()
        if productions_to_immediate:
            return productions_to_immediate._action_generate_immediate_wizard()

        for production in self:
            for final_product in production.final_product_ids:
                if float_is_zero(final_product.quantity, precision_rounding=final_product.final_product_id.uom_id.rounding):
                    raise UserError(_('The quantity to produce must be positive!'))

        consumption_issues = self._get_consumption_issues()
        if consumption_issues:
            return self._action_generate_consumption_wizard(consumption_issues)

        quantity_issues = self._get_quantity_produced_issues()
        if quantity_issues:
            return self._action_generate_backorder_wizard(quantity_issues)
        return True

    def _get_quantity_produced_issues(self):
        quantity_issues = []
        if self.env.context.get('skip_backorder', False):
            return quantity_issues
        for order in self:
            for final_product in order.final_product_ids:
                if not float_is_zero(order._get_quantity_to_backorder(), precision_rounding=final_product.final_product_id.uom_id.rounding):
                    quantity_issues.append(order)
        return quantity_issues

    def _post_inventory(self, cancel_backorder=False):
        for order in self:
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do

            finish_moves = order.move_finished_ids.filtered(lambda m:  m.state not in ('done', 'cancel'))
            # the finish move can already be completed by the workorder.
            for fm in finish_moves:
                if not fm.quantity_done:
                    fm.quantity_done = float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP')
                    fm.move_line_ids.lot_id = order.lot_producing_id
            order._cal_price(moves_to_do)

            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish._action_done(cancel_backorder=cancel_backorder)
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('move_line_ids')
            order.move_finished_ids.move_line_ids.consume_line_ids = [(6, 0, consume_move_lines.ids)]
        return True

    def action_create_qc(self):
        for rec in self:
            for final_product in rec.final_product_ids:
                self.env['quality.check'].create({
                    'product_id': final_product.final_product_id.id,
                    'production_id': final_product.production_id.id,
                    'company_id': self.company_id.id,
                    'team_id': self.env['quality.alert.team'].search([], limit=1).id,
                    'test_type_id': self.env.ref('quality_control.test_type_passfail').id,
                })

class MrpProductionLineInherit(models.Model):
    _inherit = "stock.move"

    bom_product_id = fields.Many2one('product.product', string="BoM Product")
    mo_raw_actual_qty=fields.Integer()
