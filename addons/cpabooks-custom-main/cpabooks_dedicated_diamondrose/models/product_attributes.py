from odoo import fields, models,_,api
from odoo.exceptions import ValidationError


class ProductAttribute(models.Model):
    _inherit = 'product.template'

    supplier_item_code=fields.Char(string='Supplier Item Code')
    prod_description = fields.Char(string="Product Description")

    @api.model
    def create(self,val_list):
        if 'attribute_line_ids' not in val_list.keys():
            raise ValidationError(_("Variants are mandatory for creating new product"))
        else:
            return super(ProductAttribute, self).create(val_list)
        
    # def write(self, val_list):
    #     if not self.attribute_line_ids:
    #         if 'attribute_line_ids' not in val_list.keys():
    #             raise ValidationError(_("Variants are mandatory for changing in product"))
    #     else:
    #         return super(ProductAttribute, self).write(val_list)




class SupplierItemCodeProduct(models.Model):
    _inherit = 'product.product'

    supplier_item_code = fields.Char(string='Supplier Item Code', compute='_compute_supplier_item_code_field', inverse='_set_supplier_item_code_field',store=True)
    prod_description = fields.Char(string="Product Description", compute='_compute_product_desc_field', inverse='_set_product_desc_field',store=True)

    @api.depends('product_tmpl_id.supplier_item_code')
    def _compute_supplier_item_code_field(self):
        for product in self:
            product.supplier_item_code = product.product_tmpl_id.supplier_item_code

    def _set_supplier_item_code_field(self):
        for product in self:
            product.product_tmpl_id.supplier_item_code = product.supplier_item_code

    @api.depends('product_tmpl_id.prod_description')
    def _compute_product_desc_field(self):
        for product in self:
            product.prod_description = product.product_tmpl_id.prod_description

    def _set_product_desc_field(self):
        for product in self:
            product.product_tmpl_id.prod_description = product.prod_description



