from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def get_vat_amount_in_words(self):
        if len(self.amount_by_group) >= 1:
            if len(self.amount_by_group[0]) >= 2:
                return str(self.currency_id.amount_to_text(self.amount_by_group[0][1]))
        else:
            return None