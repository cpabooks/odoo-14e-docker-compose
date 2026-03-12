from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class TemplateSettings(models.Model):
    """A model to store report template settings and styles to be applied on
    reports."""
    _inherit = "report.template.settings"

    is_item_code_visible=fields.Boolean(string="Show Item Code",default=True)