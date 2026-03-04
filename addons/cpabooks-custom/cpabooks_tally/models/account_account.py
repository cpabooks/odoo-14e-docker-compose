from odoo import api, models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    def _get_values(self):
        for rec in self:
            rec.revise = rec.name or False
            rec.proposed_code = rec.code or False
            rec.proposed_type_id = rec.user_type_id.id or False
            rec.proposed_group_id = rec.group_id.id or False

    revise = fields.Char('Proposed Account Name', compute=_get_values, readonly=False)
    proposed_code = fields.Char('Proposed Code', compute=_get_values, readonly=False)
    proposed_type_id = fields.Many2one('account.account.type', 'Proposed A/C Type', compute=_get_values, readonly=False)
    proposed_group_id = fields.Many2one('account.group', 'Proposed Group', compute=_get_values, readonly=False)

    def write(self, vals):
        if vals.get('revise'):
            vals.update({
                'name': vals.get('revise'),
                'revise': False
            })
        if vals.get('proposed_type_id'):
            vals.update({
                'user_type_id': vals.get('proposed_type_id'),
            })
        if vals.get('proposed_group_id'):
            vals.update({
                'group_id': vals.get('proposed_group_id'),
            })
        if vals.get('proposed_code'):
            vals.update({
                'code':vals.get('proposed_code')
            })
        return super(AccountAccount, self).write(vals)