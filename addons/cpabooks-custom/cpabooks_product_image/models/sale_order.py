from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    print_product_image = fields.Boolean(string="Print Product Image")
    # add_image = fields.Boolean('Add Product Image', default=True)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        if self.print_product_image:
            invoice_vals['print_product_image'] = self.print_product_image

        return invoice_vals

    @api.model
    def create(self, vals):
        record = super(SaleOrderInherit, self).create(vals)
        return record

    @api.onchange('company_id')
    def get_default_print_image(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.print_product_image = get_highest_qt.print_product_image

    @api.onchange('print_product_image')
    def _onchange_print_image(self):
        for rec in self:
            template_settings = self.env['report.template.settings'].search([], limit=1)
            if rec.print_product_image:
                template_settings.write({'show_img': True})
            if not rec.print_product_image:
                template_settings.write({'show_img': False})


