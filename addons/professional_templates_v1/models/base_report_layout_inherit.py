from odoo import api, fields, models


class CustomBaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(CustomBaseDocumentLayout, self)._onchange_company_id()

        # Custom logic to assign the "Boxed" layout as the default report layout
        boxed_layout = self.env['report.layout'].search([('name', '=', 'Boxed')], limit=1)
        if boxed_layout:
            self.report_layout_id = boxed_layout