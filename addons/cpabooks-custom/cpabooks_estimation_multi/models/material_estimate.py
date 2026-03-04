from odoo import api, fields, models, tools, _


class MaterialEstimateInherit(models.Model):
    _inherit = "material.estimate"

    bom_product_id=fields.Many2one('product.product',string="BoM Product")
    flag_field=fields.Boolean(default=True)
    @api.onchange("flag_field")
    def get_bom_product(self):
        for rec in self:
            if rec.material_id.material_estimation_ids and len(rec.material_id.material_estimation_ids) == 1:
                rec.bom_product_id = None
            elif not rec.material_id.material_estimation_ids:
                rec.bom_product_id = None
            else:
                for line in rec.material_id.material_estimation_ids[-2]:
                    rec.bom_product_id = line.bom_product_id.ids

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id.id
                # self.price_unit = self.product_id.list_price
                rec.price_unit = rec.product_id.standard_price
                rec.description = rec.product_id.description_sale if rec.product_id.description_sale else rec.product_id.name
            else:
                if rec.material_id.material_estimation_ids and len(rec.material_id.material_estimation_ids) == 1:
                    rec.bom_product_id = None
                elif not rec.material_id.material_estimation_ids:
                    rec.bom_product_id = None
                else:
                    for line in rec.material_id.material_estimation_ids[-2]:
                        rec.bom_product_id = line.bom_product_id
