from odoo import fields, models, api


class DeliveryNoteNumber(models.Model):
    _inherit = 'account.move'

    dn_number = fields.Char(compute='_compute_dn_number')

    def _compute_dn_number(self):
        delivery_note_number = self.env['stock.picking'].search([('origin', '=', self.invoice_origin)])
        self.dn_number = delivery_note_number.name
