from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # user_id = fields.Many2one(
    #     'res.users', string='Salesperson', index=True, tracking=2,default=None,
    #     domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])

    message_box=fields.Text(default="We thank you for inviting us to quote for the below mentioned work and have pleasure in submitting the same for your consideration." , string="Message")
    exclusion_or_inclusion=fields.Text(default="Exclusion",string="Exclusive")
    exclusion_or_inclusion_body = fields.Text(default="1. Any other works not mentioned in our BOQ",string="Exclusive Text")
    warm_regards=fields.Text(default=lambda self:self._set_default_warm_regards(),string="Warm Regards")
    bank_detail_enable = fields.Boolean('Show Bank Details on Invoice Report', default=False)
    enquiry_number = fields.Char(string='Enquiry Number')


    def _set_default_warm_regards(self):
        return  "We hope our quotation are in line with your requirements & look forward to hear from you\n\n\n\n\nFor, "+self.env.company.name

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        # user_id = None
        # if not self.env.context.get('not_self_saleperson'):
        #     user_id = user_id or self.env.uid
        # if user_id and self.user_id.id != user_id:
        #     values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param(
                'account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team']._get_default_team_id(
                domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=None)
        self.update(values)

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(SaleOrderInherit, self).default_get(fields_list)
    #     sale_ids = self._context.get('active_ids')
    #     vals = []
    #     sale_ids = self.env['sale.order'].browse(sale_ids)
    #
    #     # for sale in sale_ids:
    #     vals.append((0, 0, {
    #         # 'order_id': sale and sale.id or False,
    #         'product_id': self.env['product.product'].sudo().search([('name', '=', 'Write Service Description')],
    #                                                                 limit=1).id or False,
    #         # 'description': '',
    #         # 'quantity': 1,
    #
    #         # 'cheque_statement':None
    #     }))
    #
    #     res.update({
    #         'order_line': vals
    #     })
    #
    #     return res