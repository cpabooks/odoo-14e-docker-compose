from odoo import api, fields, models, tools, _


class FinalProduct(models.Model):
    _name = "estimation.final.product"

    final_product_id=fields.Many2one('product.product',string="Final Product")
    quantity=fields.Integer(string="Quantity",default=1)
    material_cost=fields.Float(string="Material Cost")
    labour_cost=fields.Float(string="Labour Cost")
    overhead_cost=fields.Float(string="Overhead Cost")
    profit_amount=fields.Float(string="Profit")
    amount=fields.Float(string="Total")
    job_estimate_id=fields.Many2one("job.estimate")
    final_quantity=fields.Integer(string="Final Qty")
    final_amount=fields.Float(string="Final Amount")

    @api.onchange('final_quantity')
    def set_final_amount(self):
        for rec in self:
            rec.final_amount=rec.final_quantity*rec.amount




class BomFinalProduct(models.Model):
    _name = "bom.final.product"

    final_product_id=fields.Many2one('product.product',string="Final Product")
    quantity=fields.Integer(string="Quantity",default=1)
    bom_id=fields.Many2one("mrp.bom")

class MRPFinalProduct(models.Model):
    _name = "mrp.final.product"

    final_product_id=fields.Many2one('product.product',string="Final Product")
    quantity=fields.Integer(string="Quantity",default=1)
    production_id=fields.Many2one("mrp.production")
    actual_quantity=fields.Integer()