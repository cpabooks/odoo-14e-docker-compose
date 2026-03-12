import json

from odoo import api, models, _
from odoo.tools import float_round

class ReportBomStructure(models.AbstractModel):
    _name = 'report.cpabooks_estimation_multi.report_bom_structure_multi'
    _description = 'BOM Structure Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for bom_id in docids:
            bom = self.env['mrp.bom'].browse(bom_id)
            # candidates = bom.product_id or bom.product_tmpl_id.product_variant_ids
            # quantity = float(data.get('quantity', 1))
            # for product_variant_id in candidates:
            #     if data and data.get('childs'):
            #         doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
            #     else:
            #         doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
            #     doc['report_type'] = 'pdf'
            #     doc['report_structure'] = data and data.get('report_type') or 'all'
            #     docs.append(doc)
            # if not candidates:
            #     if data and data.get('childs'):
            #         doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
            #     else:
            #         doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
            #     doc['report_type'] = 'pdf'
            #     doc['report_structure'] = data and data.get('report_type') or 'all'
            #     docs.append(doc)
            doc=self._get_bom(bom)
            docs.append(doc)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }
    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = bom_id
        company = bom.company_id or self.env.company

        lines={
            'bom': bom,
            'bom_prod_name':"",
            'currency': company.currency_id,
            'code': bom and bom.display_name or '',
            'bom_qty': 1,
        }
        # components, total = self._get_bom_lines(bom, level)
        get_estimation=self.env['job.estimate'].search([('name','=',bom.estimate_reference)])

        material_list=[]
        for material_p in get_estimation.material_estimation_ids:
            for bom_material_p in bom.bom_line_ids:
                if material_p.product_id.id==bom_material_p.product_id.id and material_p.bom_product_id.id==bom_material_p.bom_product_id.id:
                    mt={
                        "bom_product_name":bom_material_p.bom_product_id.name,
                        "material_name":material_p.product_id.name,
                        'code': material_p.product_id.code,
                        "quantity":bom_material_p.product_qty,
                        "uom": material_p.product_id.uom_id.name,
                        "product_price":bom_material_p.product_qty*(material_p.subtotal/material_p.quantity if material_p.quantity >0 else 1),
                        "bom_product_price":0.00
                    }
                    material_list.append(mt)

        lines['material'] = material_list
        # lines['material'] = bom.bom_line_ids
        fp_list=[]
        for final_p in get_estimation.final_product_ids:
            for bom_final_p in bom.final_product_ids:
                if final_p.final_product_id.id==bom_final_p.final_product_id.id:
                    fp={
                        'name':final_p.final_product_id.name,
                        'code':final_p.final_product_id.code,
                        'quantity':bom_final_p.quantity,
                        'uom':final_p.final_product_id.uom_id.name,
                        'product_price':0.00,
                        'bom_product_price':bom_final_p.quantity*final_p.amount

                    }
                    fp_list.append(fp)

        lines['final_product']=fp_list
        lines['labour_cost']=get_estimation.total_labour_estimate
        lines['overhead_cost']=get_estimation.total_overhead_estimate
        lines['profit']=(get_estimation.total_material_estimate+get_estimation.total_labour_estimate+get_estimation.total_overhead_estimate)*(get_estimation.profit_percent/100)
        # lines['final_product']=bom.final_product_ids
        # lines['total'] = total
        lines['estimate_reference'] = bom.estimate_reference if bom.estimate_reference else ''
        lines['project_id'] = bom.project_id.name if bom.project_id else ''
        lines['partner_id'] = bom.partner_id.name if bom.partner_id else ''
        return lines