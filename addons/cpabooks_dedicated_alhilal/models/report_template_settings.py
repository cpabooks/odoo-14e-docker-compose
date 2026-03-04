from odoo import api, models, fields, _

class ReportTemplateSettings(models.Model):
    _inherit = 'report.template.settings'

    stamp_visibility = fields.Float('Stamp Visibility', default='0.7')