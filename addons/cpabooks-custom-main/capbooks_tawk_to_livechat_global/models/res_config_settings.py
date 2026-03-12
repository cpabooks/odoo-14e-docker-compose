# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tawk_to_site_widget_id = fields.Char(
        string="Tawk To Site/Widget ID",
        help="Defines a site/widget ID (e.g: 5d91b5446c1dde20ed04210b/1h2ltmh2b)"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['tawk_to_site_widget_id'] = self.env['ir.config_parameter'].sudo().get_param('tawk_to_site_widget_id')
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "tawk_to_site_widget_id", self.tawk_to_site_widget_id
        )
        return res

    @api.model
    def get_tawk_to(self, id):
        return self.env['ir.config_parameter'].sudo().get_param('tawk_to_site_widget_id')
