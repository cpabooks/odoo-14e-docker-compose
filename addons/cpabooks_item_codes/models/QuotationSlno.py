from odoo import fields, models, _, api


class QuotationSlno(models.Model):
    _inherit = 'sale.order.line'

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.order_id.order_line:
                if line_rec.display_type not in ('line_section','line_note'):
                    line_rec.line_no = line_num
                    line_num += 1

    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)
