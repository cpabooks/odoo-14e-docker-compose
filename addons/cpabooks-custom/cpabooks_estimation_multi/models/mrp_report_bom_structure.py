from odoo import models, _
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        # bom_quantity = line_qty
        # if line_id:
        #     current_line = self.env['mrp.bom.line'].browse(int(line_id))
        #     bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id)
        # # Display bom components for current selected product variant
        # if product_id:
        #     product = self.env['product.product'].browse(int(product_id))
        # else:
        #     product = bom.product_id or bom.product_tmpl_id.product_variant_id
        # if product:
        #     attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
        #                                                    ('res_id', '=', product.id), '&',
        #                                                    ('res_model', '=', 'product.template'),
        #                                                    ('res_id', '=', product.product_tmpl_id.id)])
        # else:
        #     product = bom.product_tmpl_id
        #     attachments = self.env['mrp.document'].search(
        #         [('res_model', '=', 'product.template'), ('res_id', '=', product.id)])
        # operations = self._get_operation_line(bom, float_round(bom_quantity / bom.product_qty, precision_rounding=1,
        #                                                        rounding_method='UP'), 0)
        company = bom.company_id or self.env.company
        # lines = {
        #     'bom': bom,
        #     'bom_qty': bom_quantity,
        #     'bom_prod_name': product.display_name,
        #     'currency': company.currency_id,
        #     'product': product,
        #     'code': bom and bom.display_name or '',
        #     'price': product.uom_id._compute_price(product.with_company(company).standard_price,
        #                                            bom.product_uom_id) * bom_quantity,
        #     'total': sum([op['total'] for op in operations]),
        #     'level': level or 0,
        #     'operations': operations,
        #     'operations_cost': sum([op['total'] for op in operations]),
        #     'attachments': attachments,
        #     'operations_time': sum([op['duration_expected'] for op in operations])
        # }
        # bom_line_dict=dict()
        # for line in bom.bom_line_ids:
        #     if line.bom_product_id.name not in bom_line_dict.keys():
        #         bom_line_dict[line.bom_product_id.name]=list()
        #         bom_line_dict[line.bom_product_id.name].append(line)
        #     else:
        #         bom_line_dict[line.bom_product_id.name].append(line)

        lines={
            'bom': bom,
            'bom_prod_name':"",
            'currency': company.currency_id,
            'code': bom and bom.display_name or '',
            'bom_qty': 1,
        }
        components, total = self._get_bom_lines(bom, level)
        lines['material'] = bom.bom_line_ids
        lines['final_product']=bom.final_product_ids
        lines['total'] = total
        lines['estimate_reference'] = bom.estimate_reference if bom.estimate_reference else ''
        lines['project_id'] = bom.project_id.name if bom.project_id else ''
        lines['partner_id'] = bom.partner_id.name if bom.partner_id else ''
        return lines

    def _get_bom_lines(self, bom, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity =  line.product_qty

            company = bom.company_id or self.env.company
            price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).standard_price,
                                                          line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity,
                                                               line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            components.append({
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and line.child_bom_id.display_name or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': company.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                                                                ('res_model', '=', 'product.product'),
                                                                ('res_id', '=', line.product_id.id), '&',
                                                                ('res_model', '=', 'product.template'),
                                                                ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
        return components, total

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        bom = self.env['mrp.bom'].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        data = self._get_bom(bom_id=bom_id, product_id=product.id, line_qty=qty)
        # pdf_lines = get_sub_lines(bom, product, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data