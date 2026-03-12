from odoo import api, models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    print_image = fields.Boolean('Print Product Image', default=True)

    @api.onchange('company_id')
    def get_default_print_image(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.print_image = get_highest_qt.print_product_image

    @api.onchange('print_image')
    def _onchange_print_image(self):
        for rec in self:
            template_settings = self.env['report.template.settings'].search([], limit=1)
            print('status : ', template_settings)
            if rec.print_image:
                template_settings.write({'show_img': True})
            elif not rec.print_image:
                template_settings.write({'show_img': False})
