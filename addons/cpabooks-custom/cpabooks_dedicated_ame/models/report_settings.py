from odoo import _, api, fields, models

class ReportSettingsInherit(models.Model):
    _inherit = "report.template.settings"

    bank_font = fields.Selection([(str(x), str(x)) for x in range(1, 51)],
                                 string="Bank Font(px):",
                                 default='14',
                                 required=True)