from odoo import fields, models, api


DEFAULT_DATE_FORMAT_AUTOMTION = '%d/%m/%Y'
class LanguageFormInherit(models.Model):
    _inherit = "res.lang"

    date_format = fields.Char(string='Date Format', required=True, default=DEFAULT_DATE_FORMAT_AUTOMTION)


    @api.model
    def change_lang_date_format(self):
        get_all_language=self.env['res.lang'].sudo().search([])
        for rec in get_all_language:
            rec.date_format='%d/%m/%Y'


