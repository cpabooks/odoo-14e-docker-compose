from odoo import api, models, fields, _

class ReportPaymentCertificate(models.AbstractModel):
    _name = 'report.cpabooks_dedicated_alhilal.certificate_report_template'
    _description = 'Report for payment certificate'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['payment.certificate'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'payment.certificate',
            'docs': docs,
        }