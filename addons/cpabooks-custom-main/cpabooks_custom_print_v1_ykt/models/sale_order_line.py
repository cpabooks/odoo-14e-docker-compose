from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    # product_id = fields.Many2one(
    #     'product.product', string='Product',
    #     domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     change_default=True, ondelete='restrict', check_company=True,default=lambda self:self.env['product.product'].sudo().search([('name', '=', 'Write Service Description')],
    #                                                                  limit=1).id)

    uom_text = fields.Char(string="UoM")
    remarks=fields.Text(string="Remarks")

    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True,
        default=lambda self: self._get_service_product())
    image = fields.Binary(string="Image")
    image_name=fields.Char()

    @api.onchange('product_id')
    def set_uom(self):
        for rec in self:
            rec.uom_text = rec.product_id.uom_id.name

    def _get_service_product(self):
        get_product=self.env['product.product'].sudo().search([('name', '=', 'Write Service Description'),('active','=',True)],
                                                                  limit=1)
        if not get_product:
            vals={
                'name':'Write Service Description',
                'sequence':1,
                'type':'service',
                'categ_id':1,
                'sale_ok':True,
                'purchase_ok':True,
                'uom_id':1,
                'uom_po_id':1,
                'active':True,
                'invoice_policy':'order',
                'tracking':'none'
            }
            get_product_tmpl_id=self.env['product.template'].sudo().create(vals)
            get_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', get_product_tmpl_id.id),('active','=',True)],
                                                                    limit=1)
        return get_product.id


    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        res.update({'uom_text': self.uom_text })
        return res
