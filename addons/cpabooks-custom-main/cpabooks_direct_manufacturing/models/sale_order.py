from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    direct_manufacture=fields.Boolean(default=True,string="Direct Manufacture")

    def action_create_mo(self,bom_data,final_product_data,so_line):
        for rec in self:
            get_bom_line = bom_data.bom_line_ids.filtered(
                lambda x: x.bom_product_id.id == final_product_data.final_product_id.id)
            mo_id = self.env['mrp.production'].create({
                # 'product_id': self.env['product.product'].sudo().search(
                #     [('product_tmpl_id', '=', self.product_tmpl_id.id)]).id,
                # 'product_qty': self.product_qty,
                # 'product_uom_id': self.product_uom_id.id,
                'bom_id': bom_data.id,
                'project_id': bom_data.project_id.id,
                'partner_id': bom_data.partner_id.id,
                'company_id': bom_data.company_id.id,
                'bom_reference':bom_data.name
            })
            location_id=mo_id._get_default_location_src_id()
            source_location=self.env['stock.location'].search([('id','=',location_id)])
            location_dest_id=mo_id._get_default_location_dest_id()
            finished_products=self.env['product.product']
            if mo_id:
                for mt_line in get_bom_line:
                    # finished_products+=mt_line.bom_product_id
                    self.env['stock.move'].create({
                        'bom_product_id': mt_line.bom_product_id.id,
                        'product_id': mt_line.product_id.id,
                        'product_uom_qty': mt_line.product_qty*so_line.product_uom_qty,
                        # 'quantity_done': mt_line.product_qty*so_line.product_uom_qty,
                        'production_id': mo_id.id,
                        'name':mo_id.name,
                        'product_uom': mt_line.product_id.uom_id.id,
                        'location_id':source_location.id,
                        'location_dest_id':mt_line.bom_product_id.with_company(self.company_id).property_stock_production.id,
                        'raw_material_production_id':mo_id.id,
                        'company_id': rec.company_id.id,
                        'procure_method': 'make_to_stock',
                        'origin': mo_id.name,
                        'state': 'draft',
                        'warehouse_id': source_location.get_warehouse().id,
                        'group_id': mo_id.procurement_group_id.id,
                        'propagate_cancel': mo_id.propagate_cancel,
                        'mo_raw_actual_qty':mt_line.product_qty

                    })
                fp_vals = []
                for bom_line in final_product_data:
                    fp_vals.append(
                        mo_id._get_move_finished_values_multi(bom_line.final_product_id.id, bom_line.quantity, bom_line.final_product_id.uom_id.id,location_dest_id))
                    self.env['mrp.final.product'].create({
                        'final_product_id': bom_line.final_product_id.id,
                        'quantity': bom_line.quantity*so_line.product_uom_qty,
                        'production_id': mo_id.id,
                        'actual_quantity':bom_line.quantity
                    })
                finis_stock_moves=self.env['stock.move']
                for val in fp_vals:
                    finis_stock_moves+=self.env['stock.move'].create(val)
                mo_id.move_finished_ids=finis_stock_moves
            return mo_id

    def action_create_mo_for_extra(self,bom_data,final_product_data,so_line,final_product_extra_qty):
        for rec in self:
            get_bom_line = bom_data.bom_line_ids.filtered(
                lambda x: x.bom_product_id.id == final_product_data.final_product_id.id)
            mo_id = self.env['mrp.production'].create({
                # 'product_id': self.env['product.product'].sudo().search(
                #     [('product_tmpl_id', '=', self.product_tmpl_id.id)]).id,
                # 'product_qty': self.product_qty,
                # 'product_uom_id': self.product_uom_id.id,
                'bom_id': bom_data.id,
                'project_id': bom_data.project_id.id,
                'partner_id': bom_data.partner_id.id,
                'company_id': bom_data.company_id.id,
                'bom_reference':bom_data.name
            })
            location_id=mo_id._get_default_location_src_id()
            source_location=self.env['stock.location'].search([('id','=',location_id)])
            location_dest_id=mo_id._get_default_location_dest_id()
            finished_products=self.env['product.product']
            if mo_id:
                for mt_line in get_bom_line:
                    # finished_products+=mt_line.bom_product_id
                    self.env['stock.move'].create({
                        'bom_product_id': mt_line.bom_product_id.id,
                        'product_id': mt_line.product_id.id,
                        'product_uom_qty': mt_line.product_qty*final_product_extra_qty,
                        # 'quantity_done': mt_line.product_qty*so_line.product_uom_qty,
                        'production_id': mo_id.id,
                        'name':mo_id.name,
                        'product_uom': mt_line.product_id.uom_id.id,
                        'location_id':source_location.id,
                        'location_dest_id':mt_line.bom_product_id.with_company(self.company_id).property_stock_production.id,
                        'raw_material_production_id':mo_id.id,
                        'company_id': rec.company_id.id,
                        'procure_method': 'make_to_stock',
                        'origin': mo_id.name,
                        'state': 'draft',
                        'warehouse_id': source_location.get_warehouse().id,
                        'group_id': mo_id.procurement_group_id.id,
                        'propagate_cancel': mo_id.propagate_cancel,
                        'mo_raw_actual_qty':mt_line.product_qty

                    })
                fp_vals = []
                for bom_line in final_product_data:
                    fp_vals.append(
                        mo_id._get_move_finished_values_multi(bom_line.final_product_id.id, bom_line.quantity, bom_line.final_product_id.uom_id.id,location_dest_id))
                    self.env['mrp.final.product'].create({
                        'final_product_id': bom_line.final_product_id.id,
                        'quantity': bom_line.quantity*final_product_extra_qty,
                        'production_id': mo_id.id,
                        'actual_quantity':bom_line.quantity
                    })
                finis_stock_moves=self.env['stock.move']
                for val in fp_vals:
                    finis_stock_moves+=self.env['stock.move'].create(val)
                mo_id.move_finished_ids=finis_stock_moves
            return mo_id

    def action_confirm(self):
        for rec in self:
            if rec.direct_manufacture:
                for line in rec.order_line:
                    need_to_extra_manufacture=False
                    check_mo_existency=self.env['mrp.production'].sudo().search([('so_id','=',rec.id),('move_raw_ids.bom_product_id','=',line.product_id.id),
                                                                                 ('state','=','done')])

                    if check_mo_existency:
                        if check_mo_existency.final_product_ids.quantity<line.product_uom_qty:
                            need_to_extra_manufacture=True

                    if not check_mo_existency:
                        chk_product_in_bom_final_product=self.env['bom.final.product'].sudo().search([('final_product_id','=',line.product_id.id)],order='id desc',limit=1)
                        get_its_bom=chk_product_in_bom_final_product.bom_id
                        if get_its_bom:
                            mo_id=rec.action_create_mo(get_its_bom,chk_product_in_bom_final_product,line)
                            mo_id.action_confirm()
                            mo_id.qty_producing=1
                            mo_id._set_qty_producing()
                            # mo_id.move_raw_ids.quantity_done=mo_id.move_raw_ids.product_uom_qty
                            mo_id.button_mark_done()
                            mo_id.so_id=rec.id
                            mo_id.so_line_id=line.id

                    #if qty increase when sale order done to draft , extra qty manufacture below
                    if need_to_extra_manufacture:
                        final_product_extra_qty=line.product_uom_qty-check_mo_existency.final_product_ids.quantity

                        chk_product_in_bom_final_product = self.env['bom.final.product'].sudo().search(
                            [('final_product_id', '=', line.product_id.id)], order='id desc', limit=1)
                        get_its_bom = chk_product_in_bom_final_product.bom_id
                        if get_its_bom:
                            mo_id = rec.action_create_mo(get_its_bom, chk_product_in_bom_final_product, line,final_product_extra_qty)
                            mo_id.action_confirm()
                            mo_id.qty_producing = 1
                            mo_id._set_qty_producing()
                            # mo_id.move_raw_ids.quantity_done=mo_id.move_raw_ids.product_uom_qty
                            mo_id.button_mark_done()
                            mo_id.so_id = rec.id
                            mo_id.so_line_id = line.id


        return super(SaleOrderInherit, self).action_confirm()
