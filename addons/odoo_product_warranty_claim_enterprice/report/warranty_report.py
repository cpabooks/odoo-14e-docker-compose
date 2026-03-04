# -*- coding: utf-8 -*-

from odoo import api, models, fields


class WarrantyReport(models.AbstractModel):
    _name = 'report.odoo_product_warranty_claim.template_report_warranty'

    @api.model
    def _get_report_values(self,docids, data=None):
        contract = self.env['account.analytic.account'].browse(docids)
        warranty = []
        warranty.append(contract.custom_warranty_registration_ids.ids)
        docids = contract.custom_warranty_registration_ids.ids
        doc_ids = docids
        docargs = {
            'doc_ids': doc_ids,
            'doc_model': 'product.warranty.registration',
            'data': data,
            'docs': self.env['product.warranty.registration'].browse(doc_ids),
        }
        return docargs
