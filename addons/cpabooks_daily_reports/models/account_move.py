from odoo import api, models, fields, _

class AccountMove(models.Model):
    _inherit = 'account.move'



    rent_contract_id = fields.Many2one(
        'rent.contract',
        string='Rent Contract',
        domain="[('is_account_move', '=', False)]",
    )

    def _set_rent_contract_monthly_lines(self):
        get_all_bills = self.env['account.move'].search([
            ('company_id', '=', self.env.company.id),
            ('rent_contract_id', '!=', False)
        ])

        get_all_bills |= self
        contract_ids = [bill.rent_contract_id.id for bill in get_all_bills]
        get_all_rc = self.env['rent.contract'].search([]).ids
        missing = [rc_id for rc_id in get_all_rc if rc_id not in contract_ids]

        self.env['rent.contract'].browse(missing).is_account_move = False

        for rec in self:
            rec.rent_contract_id.is_account_move = True

    @api.model
    def create(self, vals_list):
        # Create the records first
        res = super(AccountMove, self).create(vals_list)

        # Then call _set_rent_contract_monthly_lines after creation
        if res.rent_contract_id:
            res._set_rent_contract_monthly_lines()

        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)

        # Call _set_rent_contract_monthly_lines after the record is written
        self._set_rent_contract_monthly_lines()

        return res
