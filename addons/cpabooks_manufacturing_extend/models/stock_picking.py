import datetime
from copy import deepcopy

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools import float_round



class StockPicking(models.Model):
    _inherit = 'stock.picking'



    def button_validate(self):
        for rec in self:
            rec.action_assign()
            for stock_move in rec.move_ids_without_package:
                if stock_move.product_id.free_qty<stock_move.product_uom_qty and stock_move.reserved_availability<stock_move.product_uom_qty and stock_move.picking_code=='outgoing':
                    if not self.env['mrp.bom'].sudo().search([('product_id', '=', stock_move.product_id.id)], limit=1):
                        raise ValidationError(
                            _(f"{stock_move.product_id.name} Product has not enough available quantity, Also no recipe/BoM found for production"))
                    else:
                        bom_data=self.env['mrp.bom'].sudo().search([('product_id', '=', stock_move.product_id.id)], limit=1)
                        get_bom_line = bom_data.bom_line_ids
                        mo_id = self.env['mrp.production'].create({
                            'product_id':stock_move.product_id.id,
                            # 'product_qty':stock_move.product_uom_qty,
                            'product_uom_id':stock_move.product_id.uom_id.id,
                            'bom_id': bom_data.id,
                            'bom_reference':bom_data.name,
                            'date_planned_start':datetime.datetime.now(),
                            'company_id': bom_data.company_id.id,
                            'picking_type_id':  self.env['stock.picking.type'].search([
                                            ('code', '=', 'mrp_operation'),
                                            ('warehouse_id.company_id', '=', rec.company_id.id),
                                        ], limit=1).id,
                            # 'qty_producing':stock_move.product_uom_qty,
                        })
                        mo_id.product_qty=stock_move.product_uom_qty-stock_move.forecast_availability
                        if mo_id:
                            finish_product_moves=mo_id._get_move_finished_values(mo_id.product_id.id, mo_id.product_qty, mo_id.product_uom_id.id)
                            finish_product_moves['picking_id']=None
                            raw_moves=[]
                            list_raw_moves=[]
                            list_finish_moves=[]
                            list_finish_moves.append((0,0,finish_product_moves))
                            mo_id.move_finished_ids=list_finish_moves
                            # self.env['stock.move'].create(finish_product_moves)
                            factor = mo_id.product_uom_id._compute_quantity(mo_id.product_qty,
                                                                                 mo_id.bom_id.product_uom_id) / mo_id.bom_id.product_qty
                            boms, lines = mo_id.bom_id.explode(mo_id.product_id, factor,
                                                                    picking_type=mo_id.bom_id.picking_type_id)
                            for bom_line, line_data in lines:
                                if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom' or \
                                        bom_line.product_id.type not in ['product', 'consu']:
                                    continue
                                operation = bom_line.operation_id.id or line_data['parent_line'] and line_data[
                                    'parent_line'].operation_id.id
                                raw_moves.append(mo_id._get_move_raw_values(
                                    bom_line.product_id,
                                    line_data['qty'],
                                    bom_line.product_uom_id,
                                    operation,
                                    bom_line
                                ))
                                for raw_values in raw_moves:
                                    raw_values['picking_id']=None
                                    list_raw_moves.append((0,0,raw_values))
                            mo_id.move_raw_ids = list_raw_moves
                            # self.env['stock.move'].create(finish_product_moves)
                                # finished_products+=mt_line.bom_product_id
                                # self.env['stock.move'].create({
                                #     'product_id': mt_line.product_id.id,
                                #     'product_uom_qty': mt_line.product_qty * stock_move.product_uom_qty,
                                #     'production_id': mo_id.id,
                                #     'name': mo_id.name,
                                #     'product_uom': mt_line.product_id.uom_id.id,
                                #     'location_id': source_location.id,
                                #     'location_dest_id': mt_line.product_id.with_company(
                                #         self.company_id).property_stock_production.id,
                                #     'raw_material_production_id': mo_id.id,
                                #     'company_id': rec.company_id.id,
                                #     'procure_method': 'make_to_stock',
                                #     'origin': mo_id.name,
                                #     'state': 'draft',
                                #     'warehouse_id': source_location.get_warehouse().id,
                                #     'group_id': mo_id.procurement_group_id.id,
                                #     'propagate_cancel': mo_id.propagate_cancel,
                                #     'picking_id':None
                                #
                                # })
                            mo_id.action_confirm()
                            mo_id.qty_producing=stock_move.product_uom_qty-stock_move.forecast_availability
                            mo_id._onchange_producing()
                            action = mo_id.with_context(debug=True).button_mark_done()
                            if not isinstance(action,bool):
                                immediate_wizard = Form(
                                    self.env['mrp.immediate.production'].with_context(**action['context']))
                                immediate_wizard.save().process()

                            stock_move.mo_id = mo_id.id
                            mo_id.do_id = stock_move.picking_id.id
                            self._cr.commit()

                            # stock_move.state='confirmed'
                            rec.action_assign()
            return super(StockPicking, self).button_validate()
                            