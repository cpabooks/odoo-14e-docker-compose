from odoo import api, models, fields, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_hide_header_footer = fields.Boolean('Hide Header Footer')


    @api.model
    def default_get(self, fields_list):
        get_last = self.env['account.move'].search([], limit=1, order="id desc")
        self.is_hide_header_footer = get_last.is_hide_header_footer
        return super(AccountMove, self).default_get(fields_list)

