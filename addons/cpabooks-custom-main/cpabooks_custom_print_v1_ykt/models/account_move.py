from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    bank_detail_enable = fields.Boolean('Show Bank Details on Invoice Report', default=False)

    print_manual_invoice=fields.Boolean(string="Print Manual Invoice?")

    manual_invoice=fields.Char(string="Manual Invoice")
    analytic_acc_ids=fields.Many2many('account.analytic.account',string="Analytic Accounts",compute="_get_analytic_acc")

    # prepare_by=fields.Many2one('res.users',string="Prepare By",default=lambda self:self.env.user.id)
    # prepare_by=fields.Many2one('res.users',string="Prepare By",default=lambda self:self._get_default_prepare_by())
    # approve_by=fields.Many2one('res.users',string="Approve By",default=lambda self:self._get_default_approve_by())

    # default_analytic_acc_ids = fields.Many2many('account.analytic.account', string="Analytic Accounts",compute="_get_analytic_acc")
    #

    # def _get_default_prepare_by(self):
    #     get_last_inv=self.env['account.move'].search([('company_id','=',self.env.company.id),('move_type','=','out_invoice')],order="id desc", limit=1)
    #     if get_last_inv:
    #         return get_last_inv.prepare_by.id
    #     else:
    #         return None

    # def _get_default_approve_by(self):
    #     get_last_inv=self.env['account.move'].search([('company_id','=',self.env.company.id),('move_type','=','out_invoice')],order="id desc", limit=1)
    #     if get_last_inv:
    #         return get_last_inv.approve_by.id
    #     else:
    #         return None

    @api.depends('invoice_line_ids')
    def _get_analytic_acc(self):
        for rec in self:
            rec.analytic_acc_ids=rec.invoice_line_ids.analytic_account_id.ids

    @api.model
    def _default_disclaimer(self):
        message = "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.\nAny discrepancies in the invoice need to be notified within 5 working days"
        return message or ''



    disclaimer = fields.Text(string='Disclaimer', default=_default_disclaimer)

