from odoo import api, models, fields, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    document_number = fields.Char('Document Number', compute='_get_document_number')

    def _get_document_number(self):
        for rec in self:
            if rec.move_id and rec.move_id.move_id:
                print(rec.move_id.move_id.name)
                rec.document_number = rec.move_id.move_id.name
            else:
                rec.document_number = False