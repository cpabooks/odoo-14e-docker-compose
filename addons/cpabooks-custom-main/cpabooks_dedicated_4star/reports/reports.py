from odoo import api, models, fields, _


class ReportInvoiceDotMatrix(models.AbstractModel):
    _name = 'report.cpabooks_dedicated_4star.invoice_line_template'
    _description = 'Report Invoice Dot Matrix'

    def _get_report_values(self, docids, data=None):
        # Get the active invoice records
        invoices = self.env['account.move'].browse(docids)
        additional_info = {}
        for inv in invoices:
            code = ''
            info_id = self.env['res.partner.extra'].sudo().search([
                ('partner_id', '=', inv.partner_id.id)
            ], limit=1)
            if info_id:
                code = info_id.customer_code
            additional_info.update({
                inv.id: {
                    'code': code
                }
            })

        data.update({
            'additional_info': additional_info
        })

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': invoices,
        }