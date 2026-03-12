from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action


class analytic_report(models.AbstractModel):
    _inherit = 'account.analytic.report'
    # _name = 'account.analytic.report'


    def _generate_analytic_account_lines(self, analytic_accounts, parent_id=False):
        lines = []

        for account in analytic_accounts:
            if account.balance!=0:
                lines.append({
                    'id': 'analytic_account_%s' % account.id,
                    'name': account.name,
                    'columns': [{'name': account.code},
                                {'name': account.partner_id.display_name},
                                {'name': self.format_value(account.balance)}],
                    'level': 4,  # todo check redesign financial reports, should be level + 1 but doesn't look good
                    'unfoldable': False,
                    'caret_options': 'account.analytic.account',
                    'parent_id': parent_id,  # to make these fold when the original parent gets folded
                })

        return lines