from odoo import fields, models, _, api

class InvoiceSlno(models.Model):
    _inherit = 'account.move.line'

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.move_id.invoice_line_ids:
                if line_rec.display_type not in ('line_section', 'line_note'):
                    line_rec.line_no = line_num
                    line_num += 1

    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)