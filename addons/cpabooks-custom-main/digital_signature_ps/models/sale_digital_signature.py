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
