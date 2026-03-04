from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action


class SaleOrder(models.AbstractModel):
    _inherit = 'sale.order'

    note=fields.Text(placeholder="Terms and Conditions",)

    t_and_c=fields.Html(default="")

    warm_regards = fields.Text(default=lambda self: self.set_default_warm_regards(), string="Warm Regards")

    show_warm_regards=fields.Boolean("Show W & R")
    show_t_and_c=fields.Boolean("Show T & C")

    global_vat_tax=fields.Many2many("account.tax",'sale_order_account_tax_rel',string="Applies Taxes")

    subject = fields.Char()


    def taxes_applies(self):
        for rec in self:
            for line in rec.order_line:
                line.tax_id=[(6,0,rec.global_vat_tax.ids)]

    @api.onchange('team_id')
    def get_default_data(self):
        # get_highest_so = self.env['sale.order'].sudo().search(
        #     [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.company_id.id)], limit=1,
        #     order='id desc')
        get_highest_so = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1,
            order='id desc')
        # if self.ids:
        #     get_highest_so = self.env['sale.order'].sudo().search(
        #         [('company_id', '=', self.company_id.id),('id','!=',self.ids[0])], limit=1,
        #         order='id desc')

        if get_highest_so:
            # self.t_and_c = get_highest_so.t_and_c
            self.show_t_and_c = get_highest_so.show_t_and_c
            self.warm_regards = get_highest_so.warm_regards
            self.show_warm_regards = get_highest_so.show_warm_regards
        else:
            # self.t_and_c = None
            self.show_t_and_c = False
            self.warm_regards = None
            self.show_warm_regards = False


    def set_default_warm_regards(self):
        return "We hope our quotation are in line with your requirements & look forward to hear from you\n\n\n\n\nFor, " + self.env.company.name