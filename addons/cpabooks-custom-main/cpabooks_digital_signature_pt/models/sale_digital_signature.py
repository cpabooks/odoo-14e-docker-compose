# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_sign_sale = fields.Boolean(String="Allow Digital Signature for Sale")
    is_confirm_sign_sale = fields.Boolean(string="Required Signature on Confirm Sale Order")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            is_sign_sale=(self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_sign_sale')),
            is_confirm_sign_sale=(
                self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_confirm_sign_sale'))
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('digital_signature.is_sign_sale', self.is_sign_sale),
        self.env['ir.config_parameter'].sudo().set_param('digital_signature.is_confirm_sign_sale',
                                                         self.is_confirm_sign_sale),


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warm_regards = fields.Text(default=lambda self: self._set_default_warm_regards(), string="Warm Regards")

    def _set_default_warm_regards(self):
        return "We hope our quotation are in line with your requirements & look forward to hear from you\n\nRegards\n\nFor, " + self.env.company.name

    @api.onchange("partner_id")
    def set_warm_regards(self):
        get_warm_regard_ref=self.env['sale.order'].sudo().search([('partner_id','=',self.partner_id.id)],order="id desc",limit=1)
        if get_warm_regard_ref:
            self.warm_regards=get_warm_regard_ref.warm_regards
        else:
            self.warm_regards="We hope our quotation are in line with your requirements & look forward to hear from you\n\nRegards\n\nFor, " + self.env.company.name

    @api.model
    def _digital_sign_sale_order(self):
        is_sign_sale = (self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_sign_sale'))
        return is_sign_sale

    @api.model
    def _confirm_sign_sale(self):
        is_confirm_sign_sale = (
            self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_confirm_sign_sale'))
        return is_confirm_sign_sale

    @api.model
    def _digital_logo_sale_order(self):
        is_sign_sale = (self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_sign_sale'))
        return is_sign_sale

    @api.model
    def _confirm_logo_sale(self):
        is_confirm_sign_sale = (
            self.env['ir.config_parameter'].sudo().get_param('digital_signature.is_confirm_sign_sale'))
        return is_confirm_sign_sale

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.confirm_sign_sale_compute:
            if self.digital_signature:
                return res
            else:
                raise UserError(_('Please add Digital Signature for confirm sale order...!'))
        else:
            return res
        return res

    @api.onchange('user_id')
    def set_sign_and_stamp(self):
        for rec in self:
            rec.digital_signature=rec.user_id.user_signature
            rec.digital_logo=rec.user_id.user_stamp

    def _get_default_sign(self):
        return self.env.user.user_signature
        # return self.user_id.user_signature

    def _get_default_logo(self):
        return self.env.user.user_stamp
        # return self.user_id.user_stamp

    def get_signature(self):
        get_signature_data = self.env['signature.setup'].search(
            [('model', '=', 'sale.order'), ('company_id', '=', self.env.company.id)])
        return get_signature_data

    digital_signature = fields.Binary(string="Digital Signature", default=_get_default_sign)
    digital_sign_sale_order_compute = fields.Text(default=_digital_sign_sale_order)
    confirm_sign_sale_compute = fields.Text(default=_confirm_sign_sale)

    digital_logo = fields.Binary(string="Digital Logo", default=_get_default_logo)
    # digital_logo_sale_order_compute = fields.Text(default=_digital_logo_sale_order)
    confirm_logo_sale_compute = fields.Text(default=_confirm_logo_sale)

    # approve_by = fields.Many2one('res.users', 'Approved By')
    # prepared_by = fields.Many2one('res.users', 'Prepared By')


    # @api.onchange('company_id')
    # def get_default_approve_and_prepared_by(self):
    #     for rec in self:
    #         last_val = self.env['sale.order'].search([], limit=1)
    #         if last_val:
    #             rec.approve_by = last_val.approve_by
    #             rec.prepared_by = last_val.prepared_by
    #         else:
    #             rec.approve_by = False
    #             rec.prepared_by = False
