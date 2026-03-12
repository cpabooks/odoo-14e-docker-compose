from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    print_product_image=fields.Boolean(string="Print Product Image")

    @api.model
    def create(self, vals):
        record = super(AccountMoveInherit, self).create(vals)
        return record

    @api.onchange('company_id')
    def get_default_print_image(self):
        for record in self:
            get_highest_sale_order = self.env['account.move'].sudo().search(
                [('company_id', '=', record.company_id.id), ('state', '!=', 'cancel')],
                limit=1,
                order='id desc')
            if get_highest_sale_order:
                record.print_product_image = get_highest_sale_order.print_product_image
    @api.onchange('print_product_image')
    def _onchange_print_image(self):
        for rec in self:
            template_settings = self.env['report.template.settings'].search([], limit=1)
            if rec.print_product_image:
                template_settings.write({'show_img': True})
            elif not rec.print_product_image:
                template_settings.write({'show_img': False})