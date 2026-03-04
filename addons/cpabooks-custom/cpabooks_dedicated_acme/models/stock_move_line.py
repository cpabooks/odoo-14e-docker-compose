from odoo import models, fields, api, _



class StockPickingOperation(models.Model):
    _inherit = 'stock.move.line'

    # remarks = fields.Text(string="Remarks")

    def _get_aggregated_product_quantities(self, **kwargs):
        """Returns dictionary of products and corresponding values of interest + hs_code

        Unfortunately because we are working with aggregated data, we have to loop through the
        aggregation to add more values to each datum. This extension adds on the hs_code value.

        returns: dictionary {same_key_as_super: {same_values_as_super, hs_code}, ...}
        """
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for aggregated_move_line in aggregated_move_lines:
            product_id = aggregated_move_line.split('_')[0]
            for move_line in self:
                if product_id == str(move_line.product_id.id):
                    product_description = move_line.product_description
                    product_remarks = move_line.move_id.remarks
                    aggregated_move_lines[aggregated_move_line]['product_description'] = product_description
                    aggregated_move_lines[aggregated_move_line]['product_remarks'] = product_remarks
        return aggregated_move_lines
