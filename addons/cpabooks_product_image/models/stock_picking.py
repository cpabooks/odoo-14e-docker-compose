from odoo import api, models, fields, _

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    print_image = fields.Boolean('Print Product Image')

    @api.model
    def create(self, vals):
        record = super(StockPicking, self).create(vals)
        return record

    @api.onchange('company_id')
    def get_default_print_image(self):
        for record in self:
            get_highest_sale_order = self.env['stock.picking'].sudo().search(
                [('company_id', '=', record.company_id.id), ('state', '!=', 'cancel')],
                limit=1,
                order='id desc')
            if get_highest_sale_order:
                record.print_product_image = get_highest_sale_order.print_product_image

    @api.onchange('print_image')
    def _onchange_print_image(self):
        for rec in self:
            template_settings = self.env['report.template.settings'].search([], limit=1)
            if rec.print_image:
                template_settings.write({'show_img': True})
            elif not rec.print_image:
                template_settings.write({'show_img': False})
