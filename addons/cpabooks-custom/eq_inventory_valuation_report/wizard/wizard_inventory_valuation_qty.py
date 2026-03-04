# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
from datetime import datetime, date
from odoo.tools.misc import formatLang


class wizard_inventory_valuation_qty(models.TransientModel):
    _name = 'wizard.inventory.valuation.qty'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse',)
    location_ids = fields.Many2many('stock.location', string='Location')
    start_date = fields.Date(string="Start Date") #,default= date.today().replace(day=1)
    end_date = fields.Date(string="End Date") #,default= date.today()
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Category')], string="Filter By")
    group_by_categ = fields.Boolean(string="Group By Category")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='File Name', readonly=True)
    data = fields.Binary(string='File', readonly=True)
    product_ids = fields.Many2many('product.product', string="Products")
    category_ids = fields.Many2many('product.category', string="Categories")

    # def get_companies(self):
    #     for rec in self:
    #         return [('id','in',self.env.user.company_ids.ids)]

    @api.onchange('company_id')
    def set_warehouse(self):
        for rec in self:
            warehouse_ids = self.env['stock.warehouse'].search([('id', '=', 2)])
            rec.warehouse_ids = warehouse_ids.ids

    @api.onchange('company_id')
    def onchange_company_id(self):
        # domain = [('id', 'in', self.env.user.company_ids.ids)]
        # if self.company_id:
        #     self.warehouse_ids = False
        #     self.location_ids = False
        # return {'domain':{'company_id':domain}}

        domain = [('id', '=', self.env.company.id)]
        if self.company_id:
            self.warehouse_ids = False
            self.location_ids = False
        return {'domain': {'company_id': domain}}

    @api.onchange('warehouse_ids')
    def onchange_warehouse_ids(self):
        stock_location_obj = self.env['stock.location']
        location_ids = stock_location_obj.search([('usage', '=', 'internal'), ('company_id', '=', self.company_id.id)])
        addtional_ids = []
        if self.warehouse_ids:
            for warehouse in self.warehouse_ids:
                addtional_ids.extend([y.id for y in stock_location_obj.search(
                    [('location_id', 'child_of', warehouse.view_location_id.id), ('usage', '=', 'internal')])])
            self.location_ids = False
        return {'domain': {'location_ids': [('id', 'in', addtional_ids)]}}

    def check_date_range(self):
        if self.end_date < self.start_date:
            raise ValidationError(_('End Date should be greater than Start Date.'))

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        self.product_ids = False
        self.category_ids = False

    def print_report(self):
        self.check_date_range()
        print("print_report wizard")
        datas = {'form':
            {
                'company_id': self.company_id.id,
                'warehouse_ids': [y.id for y in self.warehouse_ids],
                'location_ids': self.location_ids.ids or False,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'id': self.id,
                'product_ids': self.product_ids.ids,
                'product_categ_ids': self.category_ids.ids
            },
        }
        return self.env.ref('eq_inventory_valuation_report.action_inventory_valuation_template').report_action(self,
                                                                                                                   data=datas)

    def go_back(self):
        self.state = 'choose'
        return {
            'name': 'Inventory Valuation Report',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def print_xls_report(self):
        self.check_date_range()
        xls_filename = 'inventory_valuation_report_qty.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_filename)
        # workbook = xlsxwriter.Workbook(xls_filename)
        report_stock_inv_obj = self.env['inventory.valuation.report.qty']

        header_merge_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', \
                                                   'font_size': 10, 'bg_color': '#D3D3D3', 'border': 1})

        header_data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', \
                                                  'font_size': 10, 'border': 1})

        product_header_format = workbook.add_format({'valign': 'vcenter', 'font_size': 10, 'border': 1})

        for warehouse in self.warehouse_ids:
            worksheet = workbook.add_worksheet(warehouse.name)
            worksheet.merge_range(0, 0, 2, 8, "Inventory Valuation Report", header_merge_format)

            worksheet.set_column('A:B', 15)
            worksheet.set_column('C:C', 13)
            worksheet.write(5, 0, 'Company', header_merge_format)
            worksheet.write(5, 1, 'Warehouse', header_merge_format)
            worksheet.write(5, 2, 'Start Date', header_merge_format)
            worksheet.write(5, 3, 'End Date', header_merge_format)

            worksheet.write(6, 0, self.company_id.name, header_data_format)
            worksheet.write(6, 1, warehouse.name, header_data_format)
            worksheet.write(6, 2, str(self.start_date), header_data_format)
            worksheet.write(6, 3, str(self.end_date), header_data_format)

            if not self.location_ids:
                worksheet.set_column('D:H', 8)
                worksheet.merge_range(9, 0, 9, 2, "Products", header_merge_format)
                # worksheet.write(9, 2, "Costing Method", header_merge_format)
                worksheet.merge_range(9, 3, 9, 4, "Beginning", header_merge_format)
                worksheet.merge_range(9, 5, 9, 6, "Inbound", header_merge_format)
                worksheet.merge_range(9, 7, 9, 8, "Outbound", header_merge_format)
                # worksheet.merge_range(9, 9, 9, 10, "Internal", header_merge_format)
                # worksheet.merge_range(9, 11, 9, 12, "Adjustments", header_merge_format)
                worksheet.merge_range(9, 9, 9, 10, "Ending", header_merge_format)
                worksheet.merge_range(10, 3, 10, 4, "Qty", header_merge_format)
                worksheet.merge_range(10, 5, 10, 6, "Qty", header_merge_format)
                worksheet.merge_range(10, 7, 10, 8, "Qty", header_merge_format)
                worksheet.merge_range(10, 9, 10, 10, "Qty", header_merge_format)
                # worksheet.merge_range(10, 11, 10, 12, "Qty", header_merge_format)
                # worksheet.merge_range(10, 13, 10, 14, "Qty", header_merge_format)

                rows = 11
                prod_beginning_qty = prod_qty_in = prod_qty_out = prod_qty_int = prod_qty_adjust = prod_ending_qty = 0.00
                prod_beginning_qty_val = prod_qty_in_val = prod_qty_out_val = prod_qty_int_val = prod_qty_adjust_val = prod_ending_qty_val = 0.00
                if not self.group_by_categ:
                    for product in report_stock_inv_obj._get_products(self):
                        beginning_qty = report_stock_inv_obj._get_beginning_inventory(self, product, warehouse)
                        beginning_qty_val = report_stock_inv_obj.get_product_valuation(self, product, beginning_qty,
                                                                                       warehouse, 'beg')
                        product_val = report_stock_inv_obj.get_product_sale_qty(self, warehouse, product)
                        product_qty_in = product_val.get('product_qty_in')
                        product_qty_in_val = report_stock_inv_obj.get_product_valuation(self, product, product_qty_in,
                                                                                        warehouse, 'in')
                        product_qty_out = product_val.get('product_qty_out')
                        product_qty_out_val = report_stock_inv_obj.get_product_valuation(self, product, product_qty_out,
                                                                                         warehouse, 'out')
                        # product_qty_internal = product_val.get('product_qty_internal')
                        # product_qty_internal_val = report_stock_inv_obj.get_product_valuation(self, product,
                        #                                                                       product_qty_internal,
                        #                                                                       warehouse, 'int')
                        # product_qty_adjustment = product_val.get('product_qty_adjustment')
                        # product_qty_adjustment_val = report_stock_inv_obj.get_product_valuation(self, product,
                        #                                                                         product_qty_adjustment,
                        #                                                                         warehouse, 'adj')

                        ending_qty = beginning_qty + product_qty_in + product_qty_out

                        ending_qty_val = (
                                    beginning_qty_val + product_qty_in_val + product_qty_out_val)
                        # ending_qty_val = report_stock_inv_obj.get_product_valuation(self,product,ending_qty,warehouse)

                        worksheet.merge_range(rows, 0, rows, 2, product.display_name, product_header_format)
                        cost_method = dict(product.categ_id.fields_get()['property_cost_method']['selection'])[
                            product.categ_id.property_cost_method]
                        # worksheet.write(rows, 2, cost_method, header_data_format)
                        worksheet.merge_range(rows, 3, rows, 4, '-' if beginning_qty == 0 else beginning_qty,
                                              header_data_format)
                        worksheet.merge_range(rows, 5, rows, 6, '-' if product_qty_in == 0 else product_qty_in,
                                              header_data_format)
                        worksheet.merge_range(rows, 7, rows, 8,
                                              '-' if abs(product_qty_out) == 0 else abs(product_qty_out),
                                              header_data_format)
                        # worksheet.merge_range(rows, 9, rows, 10,
                        #                       '-' if product_qty_internal == 0 else product_qty_internal,
                        #                       header_data_format)
                        # worksheet.merge_range(rows, 11, rows, 12,
                        #                       '-' if product_qty_adjustment == 0 else product_qty_adjustment,
                        #                       header_data_format)
                        worksheet.merge_range(rows, 9, rows, 10, '-' if ending_qty == 0 else ending_qty,
                                              header_data_format)

                        prod_beginning_qty += beginning_qty
                        prod_beginning_qty_val += beginning_qty_val
                        prod_qty_in += product_qty_in
                        prod_qty_in_val += product_qty_in_val
                        prod_qty_out += product_qty_out
                        prod_qty_out_val += product_qty_out_val
                        # prod_qty_int += product_qty_internal
                        # prod_qty_int_val += product_qty_internal_val
                        # prod_qty_adjust += product_qty_adjustment
                        # prod_qty_adjust_val += product_qty_adjustment_val
                        prod_ending_qty += ending_qty
                        prod_ending_qty_val += ending_qty_val
                        rows += 1

                    worksheet.merge_range(rows + 1, 0, rows + 1, 2, 'Total', header_merge_format)
                    worksheet.merge_range(rows + 1, 3, rows + 1, 4,
                                          '-' if prod_beginning_qty == 0 else prod_beginning_qty, header_merge_format)
                    worksheet.merge_range(rows + 1, 5, rows + 1, 6, '-' if prod_qty_in == 0 else prod_qty_in,
                                          header_merge_format)
                    worksheet.merge_range(rows + 1, 7, rows + 1, 8,
                                          '-' if abs(prod_qty_out) == 0 else abs(prod_qty_out), header_merge_format)
                    # worksheet.merge_range(rows + 1, 9, rows + 1, 10, '- ' if prod_qty_int == 0 else prod_qty_int,
                    #                       header_merge_format)
                    # worksheet.merge_range(rows + 1, 11, rows + 1, 12, '-' if prod_qty_adjust == 0 else prod_qty_adjust,
                    #                       header_merge_format)
                    worksheet.merge_range(rows + 1, 9, rows + 1, 10, '-' if prod_ending_qty == 0 else prod_ending_qty,
                                          header_merge_format)

                else:
                    rows += 1
                    product_val = report_stock_inv_obj.get_product_sale_qty(self, warehouse)
                    for categ, product_value in product_val.items():
                        categ_prod_beginning_qty = categ_prod_qty_in = categ_prod_qty_out = categ_prod_qty_int = categ_prod_qty_adjust = categ_prod_ending_qty = 0.00
                        categ_prod_beginning_qty_val = categ_prod_qty_in_val = categ_prod_qty_out_val = categ_prod_qty_int_val = categ_prod_qty_adjust_val = categ_prod_ending_qty_val = 0.00
                        worksheet.merge_range(rows, 0, rows, 14, self.env['product.category'].browse(categ).name,
                                              header_merge_format)
                        rows += 1
                        for product in product_value:
                            product_id = self.env['product.product'].browse(product['product_id'])
                            beginning_qty = report_stock_inv_obj._get_beginning_inventory(self, product_id.id,
                                                                                          warehouse)
                            beginning_qty_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                           beginning_qty, warehouse,
                                                                                           'beg')
                            product_qty_in = product.get('product_qty_in')
                            product_qty_in_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                            product_qty_in, warehouse,
                                                                                            'in')
                            product_qty_out = product.get('product_qty_out')
                            product_qty_out_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                             product_qty_out, warehouse,
                                                                                             'out')
                            # product_qty_internal = product.get('product_qty_internal')
                            # product_qty_internal_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                            #                                                                       product_qty_internal,
                            #                                                                       warehouse, 'int')
                            # product_qty_adjustment = product.get('product_qty_adjustment')
                            # product_qty_adjustment_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                            #                                                                         product_qty_adjustment,
                            #                                                                         warehouse, 'adj')
                            ending_qty = beginning_qty + product_qty_in + product_qty_out
                            ending_qty_val = (
                                        beginning_qty_val + product_qty_in_val + product_qty_out_val)

                            worksheet.merge_range(rows, 0, rows, 2, product_id.display_name, product_header_format)
                            cost_method = dict(product_id.categ_id.fields_get()['property_cost_method']['selection'])[
                                product_id.categ_id.property_cost_method]
                            # worksheet.write(rows, 2, cost_method, header_data_format)

                            worksheet.merge_range(rows, 3, rows, 4, '-' if beginning_qty == 0 else beginning_qty,
                                                  header_data_format)
                            worksheet.merge_range(rows, 5, rows, 6, '- ' if product_qty_in == 0 else product_qty_in,
                                                  header_data_format)
                            worksheet.merge_range(rows, 7, rows, 8,
                                                  '-' if abs(product_qty_out) == 0 else abs(product_qty_out),
                                                  header_data_format)
                            # worksheet.merge_range(rows, 9, rows, 10,
                            #                       '-' if product_qty_internal == 0 else product_qty_internal,
                            #                       header_data_format)
                            # worksheet.merge_range(rows, 11, rows, 12,
                            #                       '-' if product_qty_adjustment == 0 else product_qty_adjustment,
                            #                       header_data_format)
                            worksheet.merge_range(rows, 9, rows, 10, '-' if ending_qty == 0 else ending_qty,
                                                  header_data_format)

                            categ_prod_beginning_qty += beginning_qty
                            categ_prod_qty_in += product_qty_in
                            categ_prod_qty_out += product_qty_out
                            # categ_prod_qty_int += product_qty_internal
                            # categ_prod_qty_adjust += product_qty_adjustment
                            categ_prod_ending_qty += ending_qty

                            categ_prod_beginning_qty_val += beginning_qty_val
                            categ_prod_qty_in_val += product_qty_in_val
                            categ_prod_qty_out_val += product_qty_out_val
                            # categ_prod_qty_int_val += product_qty_internal_val
                            # categ_prod_qty_adjust_val += product_qty_adjustment_val
                            categ_prod_ending_qty_val += ending_qty_val
                            rows += 1

                        worksheet.merge_range(rows, 0, rows, 1, 'Total', header_merge_format)
                        worksheet.merge_range(rows, 3, rows, 4, categ_prod_beginning_qty, header_merge_format)
                        worksheet.merge_range(rows, 5, rows, 6, categ_prod_qty_in, header_merge_format)
                        worksheet.merge_range(rows, 7, rows, 8, abs(categ_prod_qty_out), header_merge_format)
                        # worksheet.merge_range(rows, 9, rows, 10, categ_prod_qty_int, header_merge_format)
                        # worksheet.merge_range(rows, 11, rows, 12, categ_prod_qty_adjust, header_merge_format)
                        worksheet.merge_range(rows, 9, rows, 10, categ_prod_ending_qty, header_merge_format)

                        prod_qty_in += categ_prod_qty_in
                        prod_qty_out += categ_prod_qty_out
                        # prod_qty_int += categ_prod_qty_int
                        # prod_qty_adjust += categ_prod_qty_adjust
                        prod_ending_qty += categ_prod_ending_qty
                        prod_beginning_qty += categ_prod_beginning_qty

                        prod_beginning_qty_val += categ_prod_beginning_qty_val
                        prod_qty_in_val += categ_prod_qty_in_val
                        prod_qty_out_val += categ_prod_qty_out_val
                        # prod_qty_int_val += categ_prod_qty_int_val
                        # prod_qty_adjust_val += categ_prod_qty_adjust_val
                        prod_ending_qty_val += categ_prod_ending_qty_val
                        rows += 2

            else:
                worksheet.set_column('D:D', 9)
                worksheet.set_column('E:H', 5)
                worksheet.merge_range(9, 0, 9, 2, "Products", header_merge_format)
                # worksheet.write(9, 2, "Costing Method", header_merge_format)
                worksheet.write(9, 3, "Location", header_merge_format)
                worksheet.merge_range(9, 4, 9, 5, "Beginning", header_merge_format)
                worksheet.merge_range(9, 6, 9, 7, "Inbound", header_merge_format)
                worksheet.merge_range(9, 8, 9, 9, "Outbound", header_merge_format)
                # worksheet.merge_range(9, 10, 9, 11, "Internal", header_merge_format)
                # worksheet.merge_range(9, 12, 9, 13, "Adjustments", header_merge_format)
                worksheet.merge_range(9, 10, 9, 11, "Ending", header_merge_format)
                worksheet.merge_range(10, 4, 10, 5, "Qty", header_merge_format)
                worksheet.merge_range(10, 6, 10, 7, "Qty", header_merge_format)
                worksheet.merge_range(10, 8, 10, 9, "Qty", header_merge_format)
                # worksheet.merge_range(10, 10, 10, 11, "Qty", header_merge_format)
                # worksheet.merge_range(10, 12, 10, 13, "Qty", header_merge_format)
                worksheet.merge_range(10, 10, 10, 11, "Qty", header_merge_format)

                rows = 11
                prod_beginning_qty = prod_qty_in = prod_qty_out = prod_qty_int = prod_qty_adjust = prod_ending_qty = 0.00
                prod_beginning_qty_val = prod_qty_in_val = prod_qty_out_val = prod_qty_int_val = prod_qty_adjust_val = prod_ending_qty_val = 0.00
                location_ids = report_stock_inv_obj.get_warehouse_wise_location(self, warehouse)
                if not self.group_by_categ:
                    for product in report_stock_inv_obj._get_products(self):
                        location_wise_data = report_stock_inv_obj.get_location_wise_product(self, warehouse, product,
                                                                                            location_ids)
                        beginning_qty = location_wise_data[1][0]
                        beginning_qty_val = report_stock_inv_obj.get_product_valuation(self, product, beginning_qty,
                                                                                       warehouse, 'beg')
                        # print(beginning_qty)
                        # print(f'val {beginning_qty_val}')
                        product_qty_in = location_wise_data[1][1]
                        product_qty_in_val = report_stock_inv_obj.get_product_valuation(self, product, product_qty_in,
                                                                                        warehouse, 'in')
                        product_qty_out = location_wise_data[1][2]
                        product_qty_out_val = report_stock_inv_obj.get_product_valuation(self, product, product_qty_out,
                                                                                         warehouse, 'out')
                        # product_qty_internal = location_wise_data[1][3]
                        # product_qty_internal_val = report_stock_inv_obj.get_product_valuation(self, product,
                        #                                                                       product_qty_internal,
                        #                                                                       warehouse, 'int')
                        # product_qty_adjustment = location_wise_data[1][4]
                        # product_qty_adjustment_val = report_stock_inv_obj.get_product_valuation(self, product,
                        #                                                                         product_qty_adjustment,
                        #                                                                         warehouse, 'adj')
                        ending_qty = (beginning_qty + product_qty_in + product_qty_out)
                        print(f'end {ending_qty}')
                        # ending_qty_val = report_stock_inv_obj.get_product_valuation(self, product, ending_qty,
                        #                                                             warehouse, 'final')
                        ending_qty_val = beginning_qty_val + product_qty_in_val + product_qty_out_val

                        worksheet.merge_range(rows, 0, rows, 2, product.display_name, product_header_format)
                        cost_method = dict(product.categ_id.fields_get()['property_cost_method']['selection'])[
                            product.categ_id.property_cost_method]
                        # worksheet.write(rows, 2, cost_method, header_data_format)
                        worksheet.write(rows, 3, ' ', header_data_format)
                        worksheet.merge_range(rows, 4, rows, 5, '-' if beginning_qty == 0 else beginning_qty,
                                              header_merge_format)
                        worksheet.merge_range(rows, 6, rows, 7, '-' if product_qty_in == 0 else product_qty_in,
                                              header_merge_format)
                        worksheet.merge_range(rows, 8, rows, 9,
                                              '-' if abs(product_qty_out) == 0 else abs(product_qty_out),
                                              header_merge_format)
                        # worksheet.merge_range(rows, 10, rows, 11,
                        #                       '-' if product_qty_internal == 0 else product_qty_internal,
                        #                       header_merge_format)
                        # worksheet.merge_range(rows, 12, rows, 13,
                        #                       '-' if product_qty_adjustment == 0 else product_qty_adjustment,
                        #                       header_merge_format)
                        worksheet.merge_range(rows, 10, rows, 11, '-' if ending_qty == 0 else ending_qty,
                                              header_merge_format)
                        rows += 1

                        for location, value in location_wise_data[0].items():
                            worksheet.merge_range(rows, 0, rows, 2, '', header_data_format)
                            worksheet.write(rows, 3, location.display_name, header_data_format)
                            worksheet.merge_range(rows, 4, rows, 5, '-' if value[0] == 0 else value[0],
                                                  header_data_format)
                            worksheet.merge_range(rows, 6, rows, 7, '-' if value[1] == 0 else value[1],
                                                  header_data_format)
                            worksheet.merge_range(rows, 8, rows, 9, '-' if abs(value[2]) == 0 else abs(value[2]),
                                                  header_data_format)
                            # worksheet.merge_range(rows, 10, rows, 11, '-' if value[3] == 0 else value[3],
                            #                       header_data_format)
                            # worksheet.merge_range(rows, 12, rows, 13, '-' if value[4] == 0 else value[4],
                            #                       header_data_format)
                            worksheet.merge_range(rows, 10, rows, 11, '-' if value[5] == 0 else value[5],
                                                  header_data_format)
                            rows += 1

                        prod_beginning_qty += beginning_qty
                        prod_beginning_qty_val += beginning_qty_val
                        prod_qty_in += product_qty_in
                        prod_qty_in_val += product_qty_in_val
                        prod_qty_out += product_qty_out
                        prod_qty_out_val += product_qty_out_val
                        # prod_qty_int += product_qty_internal
                        # prod_qty_int_val += product_qty_internal_val
                        # prod_qty_adjust += product_qty_adjustment
                        # prod_qty_adjust_val += product_qty_adjustment_val
                        prod_ending_qty += ending_qty
                        prod_ending_qty_val += ending_qty_val

                    rows += 1
                    worksheet.merge_range(rows, 0, rows, 3, 'Total', header_merge_format)
                    worksheet.merge_range(rows, 4, rows, 5, '-' if prod_beginning_qty == 0 else prod_beginning_qty,
                                          header_merge_format)
                    worksheet.merge_range(rows, 6, rows, 7, '-' if prod_qty_in == 0 else prod_qty_in,
                                          header_merge_format)
                    worksheet.merge_range(rows, 8, rows, 9, '-' if abs(prod_qty_out) == 0 else abs(prod_qty_out),
                                          header_merge_format)
                    # worksheet.merge_range(rows, 10, rows, 11, '-' if prod_qty_int == 0 else prod_qty_int,
                    #                       header_merge_format)
                    # worksheet.merge_range(rows, 12, rows, 13, '-' if prod_qty_adjust == 0 else prod_qty_adjust,
                    #                       header_merge_format)
                    worksheet.merge_range(rows, 10, rows, 11, '-' if prod_ending_qty == 0 else prod_ending_qty,
                                          header_merge_format)

                else:
                    rows += 1
                    product_val = report_stock_inv_obj.get_product_sale_qty(self, warehouse)
                    for categ, product_value in product_val.items():
                        categ_prod_beginning_qty = categ_prod_qty_in = categ_prod_qty_out = categ_prod_qty_int = categ_prod_qty_adjust = categ_prod_ending_qty = 0.00
                        categ_prod_beginning_qty_val = categ_prod_qty_in_val = categ_prod_qty_out_val = categ_prod_qty_int_val = categ_prod_qty_adjust_val = categ_prod_ending_qty_val = 0.00
                        worksheet.merge_range(rows, 0, rows, 15, self.env['product.category'].browse(categ).name,
                                              header_merge_format)
                        rows += 1
                        for product in product_value:
                            product_id = self.env['product.product'].browse(product['product_id'])
                            location_wise_data = report_stock_inv_obj.get_location_wise_product(self, warehouse,
                                                                                                product_id,
                                                                                                location_ids)
                            beginning_qty = location_wise_data[1][0]
                            beginning_qty_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                           beginning_qty, warehouse,
                                                                                           'beg')
                            product_qty_in = location_wise_data[1][1]
                            product_qty_in_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                            product_qty_in, warehouse,
                                                                                            'in')
                            product_qty_out = abs(location_wise_data[1][2])
                            product_qty_out_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                                                                                             product_qty_out, warehouse,
                                                                                             'out')
                            # product_qty_internal = location_wise_data[1][3]
                            # product_qty_internal_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                            #                                                                       product_qty_internal,
                            #                                                                       warehouse, 'int')
                            # product_qty_adjustment = location_wise_data[1][4]
                            # product_qty_adjustment_val = report_stock_inv_obj.get_product_valuation(self, product_id,
                            #                                                                         product_qty_adjustment,
                            #                                                                         warehouse, 'adj')
                            ending_qty = beginning_qty + product_qty_in + product_qty_out
                            ending_qty_val = beginning_qty_val + product_qty_in_val + product_qty_out_val

                            worksheet.merge_range(rows, 0, rows, 2, product_id.display_name, product_header_format)
                            cost_method = dict(product_id.categ_id.fields_get()['property_cost_method']['selection'])[
                                product_id.categ_id.property_cost_method]
                            # worksheet.write(rows, 2, cost_method, header_data_format)
                            worksheet.write(rows, 3, ' ', header_data_format)
                            worksheet.merge_range(rows, 4, rows, 5, '-' if beginning_qty == 0 else beginning_qty,
                                                  header_merge_format)

                            worksheet.merge_range(rows, 6, rows, 7, '-' if product_qty_in == 0 else product_qty_in,
                                                  header_merge_format)

                            worksheet.merge_range(rows, 8, rows, 9,
                                                  '-' if abs(product_qty_out) == 0 else abs(product_qty_out),
                                                  header_merge_format)

                            # worksheet.merge_range(rows, 10, rows, 11,
                            #                       '-' if product_qty_internal == 0 else product_qty_internal,
                            #                       header_merge_format)
                            #
                            # worksheet.merge_range(rows, 12, rows, 13,
                            #                       '-' if product_qty_adjustment == 0 else product_qty_adjustment,
                            #                       header_merge_format)

                            worksheet.merge_range(rows, 10, rows, 11, '-' if ending_qty == 0 else ending_qty,
                                                  header_merge_format)

                            rows += 1

                            for location, value in location_wise_data[0].items():
                                worksheet.merge_range(rows, 0, rows, 2, '', header_data_format)
                                worksheet.write(rows, 3, location.display_name, header_data_format)
                                worksheet.merge_range(rows, 4, rows, 5, '-' if value[0] == 0 else value[0],
                                                      header_data_format)
                                worksheet.merge_range(rows, 6, rows, 7, '-' if value[1] == 0 else value[1],
                                                      header_data_format)
                                worksheet.merge_range(rows, 8, rows, 9, '-' if abs(value[2]) == 0 else abs(value[2]),
                                                      header_data_format)
                                # worksheet.merge_range(rows, 10, rows, 11, '-' if value[3] == 0 else value[3],
                                #                       header_data_format)
                                # worksheet.merge_range(rows, 12, rows, 13, '-' if value[4] == 0 else value[4],
                                #                       header_data_format)
                                worksheet.merge_range(rows, 10, rows, 11, '-' if value[5] == 0 else value[5],
                                                      header_data_format)
                                rows += 1

                            categ_prod_beginning_qty += beginning_qty
                            categ_prod_qty_in += product_qty_in
                            categ_prod_qty_out += product_qty_out
                            # categ_prod_qty_int += product_qty_internal
                            # categ_prod_qty_adjust += product_qty_adjustment
                            categ_prod_ending_qty += ending_qty

                            categ_prod_beginning_qty_val += beginning_qty_val
                            categ_prod_qty_in_val += product_qty_in_val
                            categ_prod_qty_out_val += product_qty_out_val
                            # categ_prod_qty_int_val += product_qty_internal_val
                            # categ_prod_qty_adjust_val += product_qty_adjustment_val
                            categ_prod_ending_qty_val += ending_qty_val

                        worksheet.merge_range(rows, 0, rows, 1, 'Total', header_merge_format)
                        worksheet.merge_range(rows, 4, rows, 5,
                                              '-' if categ_prod_beginning_qty == 0 else categ_prod_beginning_qty,
                                              header_merge_format)
                        worksheet.merge_range(rows, 6, rows, 7, '-' if categ_prod_qty_in == 0 else categ_prod_qty_in,
                                              header_merge_format)
                        worksheet.merge_range(rows, 8, rows, 9,
                                              '-' if abs(categ_prod_qty_out) == 0 else abs(categ_prod_qty_out),
                                              header_merge_format)
                        # worksheet.merge_range(rows, 10, rows, 11, '-' if categ_prod_qty_int == 0 else categ_prod_qty_in,
                        #                       header_merge_format)
                        # worksheet.merge_range(rows, 12, rows, 13,
                        #                       '-' if categ_prod_qty_adjust == 0 else categ_prod_qty_adjust,
                        #                       header_merge_format)
                        worksheet.merge_range(rows, 10, rows, 11,
                                              '-' if categ_prod_ending_qty == 0 else categ_prod_ending_qty,
                                              header_merge_format)
                        rows += 1
                        rows += 2

        workbook.close()
        self.write({
            'state': 'get',
            'data': base64.b64encode(open('/tmp/' + xls_filename, 'rb').read()),
            'name': xls_filename
        })

        # '/tmp/' +

        return {
            'name': 'Inventory Valuation Report',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: