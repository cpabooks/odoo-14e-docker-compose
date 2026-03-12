from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class MRPBomInherit(models.Model):
    _inherit = "mrp.bom"

    bom_name=fields.Char(string="BoM Name")
    # is_for_mo=fields.Boolean()
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=False)

    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Unit of Measure', required=False)

    final_product_ids=fields.One2many('bom.final.product','bom_id')

    def name_get(self):
        result = []
        for bom in self:
            # if bom._context.get('is_for_mo') == True:
            if bom.bom_name!=False:
                result.append((bom.id, bom.bom_name))
            # else:
            #     result.append((bom.id, bom.name))
        return result

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     ids = self._name_search(name, args, operator, limit=limit)
    #     return self.browse(ids).sudo().with_context(is_for_mo=True).name_get()

    @api.onchange('bom_line_ids')
    def set_final_products(self):
        for rec in self:
            flag = 0
            for fp in rec.final_product_ids:
                for mt in rec.bom_line_ids:
                    if fp.final_product_id.id == mt.bom_product_id.id:
                        flag = 1
                if flag == 0:
                    rec.final_product_ids -= fp

            for mt_line in rec.bom_line_ids:
                if mt_line.bom_product_id and mt_line.bom_product_id.id not in rec.final_product_ids.final_product_id.ids:
                    val = [(0, 0, {
                        'final_product_id': mt_line.bom_product_id.id,
                        # 'quantity':line.task_id.id,
                        # 'amount': mt_line.subtotal
                    })]
                    rec.final_product_ids = val
                else:
                    rec.final_product_ids = [(5, 0, 0)]
                    product_dict = {}
                    for mt_line in rec.bom_line_ids:
                        if mt_line.bom_product_id.id not in product_dict.keys():
                            product_dict[mt_line.bom_product_id.id] = 1
                        # else:
                        #     product_dict[mt_line.bom_product_id.id] += mt_line.subtotal

                    for p_dict in product_dict.keys():
                        val = [(0, 0, {
                            'final_product_id': p_dict,
                            'quantity':1,
                            # 'amount': product_dict[p_dict]
                        })]
                        rec.final_product_ids = val
                    # for fp_line in rec.final_product_ids:
                    #     if fp_line.final_product_id.id==mt_line.bom_product_id.id:
                    #         fp_line.amount+=mt_line.subtotal

    def action_create_mo(self):
        for rec in self:
            mo_id = self.env['mrp.production'].create({
                # 'product_id': self.env['product.product'].sudo().search(
                #     [('product_tmpl_id', '=', self.product_tmpl_id.id)]).id,
                # 'product_qty': self.product_qty,
                # 'product_uom_id': self.product_uom_id.id,
                'bom_id': rec.id,
                'project_id': rec.project_id.id,
                'partner_id': rec.partner_id.id,
                'company_id': rec.company_id.id,
                'bom_reference':rec.name
            })
            location_id=mo_id._get_default_location_src_id()
            source_location=self.env['stock.location'].search([('id','=',location_id)])
            location_dest_id=mo_id._get_default_location_dest_id()
            finished_products=self.env['product.product']
            if mo_id:
                for mt_line in rec.bom_line_ids:
                    finished_products+=mt_line.bom_product_id
                    self.env['stock.move'].create({
                        'bom_product_id': mt_line.bom_product_id.id,
                        'product_id': mt_line.product_id.id,
                        'product_uom_qty': mt_line.product_qty,
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
                for bom_line in rec.final_product_ids:
                    fp_vals.append(
                        mo_id._get_move_finished_values_multi(bom_line.final_product_id.id, bom_line.quantity, bom_line.final_product_id.uom_id.id,location_dest_id))
                    self.env['mrp.final.product'].create({
                        'final_product_id': bom_line.final_product_id.id,
                        'quantity': bom_line.quantity,
                        'production_id': mo_id.id,
                        'actual_quantity':bom_line.quantity
                    })
                finis_stock_moves=self.env['stock.move']
                for val in fp_vals:
                    finis_stock_moves+=self.env['stock.move'].create(val)
                mo_id.move_finished_ids=finis_stock_moves



            # mo_id.onchange_product_id()
            # mo_id._onchange_bom_id()
            # mo_id._onchange_move_raw()
            #
            # mo_id._compute_allowed_product_ids()
            # mo_id._onchange_move_finished()
            # mo_id._onchange_location()
            # mo_id._onchange_location_dest()
            # mo_id._onchange_workorder_ids()




class MRPBomLineInherit(models.Model):
    _inherit = "mrp.bom.line"

    bom_product_id = fields.Many2one('product.product', string="BoM Product")

