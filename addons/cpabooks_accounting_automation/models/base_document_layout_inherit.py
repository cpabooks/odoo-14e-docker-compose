from odoo import fields, models, api


# class ReportLayoutInherit(models.Model):
#         _inherit="report.layout"
        # _order = 'sequence desc'

class ResCompanyInherit(models.Model):
        _inherit = 'res.company'

        @api.model
        def action_change_report_layout_id(self):
                get_all_company=self.env['res.company'].sudo().search([])

                for rec in get_all_company:
                        rec.external_report_layout_id=self.env['ir.ui.view'].sudo().search([('name','=','external_layout_background')]).id

