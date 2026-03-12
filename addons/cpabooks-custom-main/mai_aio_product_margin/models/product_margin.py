from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    margin = fields.Float('Margin %', compute='compute_margin' , readonly=True)
    # list_price = fields.Float('Sale Price', digits='Product Price')
    # standard_price = fields.Float(digits='Product Price',groups="base.group_user", string="Cost Price")


    def compute_margin(self):
        for product in self:
            result = 0
            if product.list_price == 0 or product.standard_price == 0:
                result = 0
            else:
                result = ((product.list_price - product.standard_price) / product.list_price) * 100
            product.update({'margin' : result})

    # def compute_margin(self):
    #     for rec in self:
    #         if rec.lst_price and rec.standard_price:
    #             list_price = rec.lst_price
    #             rec.price_notax = rec.lst_price
    #             if rec.taxes_id:
    #                 total_excluded = 0
    #                 for tax_id in rec.taxes_id:
    #                     tax_data = tax_id.compute_all(rec.list_price)
    #                     total_excluded += tax_data['total_excluded']
    #                 list_price = total_excluded
    #                 rec.price_notax = total_excluded
    #             rec.prdct_mrgn = ((list_price - rec.standard_price) / rec.standard_price) * 100
    #         else:
    #             rec.prdct_mrgn = 0


class ProductProduct(models.Model):
    _inherit = "product.product"

    margin = fields.Float('Margin %', compute='compute_margin' , readonly=True)
    # list_price = fields.Float('Sale Price', digits='Product Price')
    # standard_price = fields.Float(digits='Product Price',groups="base.group_user", string="Cost Price")


    def compute_margin(self):
        for product in self:
            result = 0
            if product.list_price == 0 or product.standard_price == 0:
                result = 0
            else:
                result = ((product.list_price - product.standard_price) / product.list_price) * 100
            product.update({'margin' : result})


    # def compute_margin(self):
    #     for rec in self:
    #         if rec.list_price and rec.standard_price:
    #             list_price = rec.list_price
    #             rec.price_notax = rec.list_price
    #             if rec.taxes_id:
    #                 total_excluded = 0
    #                 for tax_id in rec.taxes_id:
    #                     tax_data = tax_id.compute_all(rec.list_price)
    #                     total_excluded += tax_data['total_excluded']
    #                 list_price = total_excluded
    #                 rec.price_notax = total_excluded
    #             rec.prdct_mrgn = ((list_price - rec.standard_price) / rec.standard_price) * 100
    #         else:
    #             rec.prdct_mrgn = 0                     
                           

