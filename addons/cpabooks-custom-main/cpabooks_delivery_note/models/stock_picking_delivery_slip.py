from odoo import fields, models, api


class DeliveryNote(models.Model):
    _inherit = 'stock.move'

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.picking_id.move_ids_without_package:
                line_rec.line_no = line_num
                line_num += 1

    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)
