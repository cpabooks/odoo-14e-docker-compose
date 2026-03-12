from odoo import fields, models, api

class AutoDebrand(models.Model):
    _name="auto.debrand"

    @api.model
    def auto_brand_remove(self):
        # get_all_company = self.env['res.company'].sudo().search([])
        # for com in get_all_company:
        self.env['res.config.settings'].get_values()
        self.env['res.config.settings'].set_values()
        # ir_config = self.env['ir.config_parameter'].sudo()
        # ir_config.set_param("company_id", com.id)
        config_settings = self.env['res.config.settings'].create({})
        config_settings.execute()