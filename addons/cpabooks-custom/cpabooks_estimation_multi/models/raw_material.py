from odoo import api, fields, models, tools, _


class FinalProduct(models.Model):
    _name = "raw.material.summary"

    product_id=fields.Many2one('product.product',string='Product')
    quantity=fields.Float(string='Quantity')
    job_estimate_id=fields.Many2one('job.estimate')