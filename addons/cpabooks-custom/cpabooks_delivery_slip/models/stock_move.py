# -*- coding: utf-8 -*-

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    # product_description = fields.Text(string='Product Description', related='sale_line_id.name', store=True)
    product_description = fields.Text(string='Product Description', compute='_compute_product_description')

    def _compute_product_description(self):
        for record in self:
            record.product_description = ''
            if record.sale_line_id:
                record.product_description = record.sale_line_id.name
            if record.purchase_line_id:
                record.product_description = record.purchase_line_id.name


class StockPackOperation(models.Model):
    _inherit = 'stock.move.line'

    product_description = fields.Text(string='Product Description', related='move_id.product_description', store=True)

    

    def _get_aggregated_product_quantities(self, **kwargs):
        """Returns dictionary of products and corresponding values of interest + hs_code

        Unfortunately because we are working with aggregated data, we have to loop through the
        aggregation to add more values to each datum. This extension adds on the hs_code value.

        returns: dictionary {same_key_as_super: {same_values_as_super, hs_code}, ...}
        """
        already_done_move_line=self.env['stock.move.line']
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for aggregated_move_line in aggregated_move_lines:
            product_id = aggregated_move_line.split('_')[0]
            for move_line in self-already_done_move_line:
                if product_id == str(move_line.product_id.id):
                    already_done_move_line+=move_line
                    product_description = move_line.move_id.description_picking
                    aggregated_move_lines[aggregated_move_line]['product_description'] = product_description
                    break
            # aggregated_move_lines[aggregated_move_line]['product_description'] = aggregated_move_lines[aggregated_move_line]['description']
        return aggregated_move_lines
