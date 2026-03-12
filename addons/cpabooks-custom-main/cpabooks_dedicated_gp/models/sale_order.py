from num2words import num2words

from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = ["sale.order"]

    project_name = fields.Char(string="Project Name")

    @api.model
    def project_name_in_text_field(self):
        get_all_sales_order = self.env['sale.order'].sudo().search([])

        for so in get_all_sales_order:
            if so.cust_project_id:
                so.project_name = so.cust_project_id.name
                if not so.project_id:
                    so.project_id = so.cust_project_id.id


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line"]

    class_name = fields.Many2one('product.class', string="Class", compute="set_class", readonly=False, store=True)
    item_code= fields.Char(related='product_id.item_code')


    @api.depends('product_id')
    def set_class(self):
        for rec in self:
            rec.class_name = rec.product_id.product_class.id


