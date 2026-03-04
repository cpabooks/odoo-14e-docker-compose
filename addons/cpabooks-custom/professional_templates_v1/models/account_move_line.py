from odoo import api, models, fields, _


class AccountPayAccountMoveLinement(models.Model):
    _inherit = 'account.move.line'


    previous_p = fields.Float(string="Previous %")
    work_done = fields.Float(string="Work Done %")
    total_contr_amt = fields.Float(string="Amount Excl. Tax", compute="_compute_total_contr_amt")
    total_work_done = fields.Float(string="Total Amt (Wrk Done)", compute="_compute_total_work_done")
    tax_amt = fields.Float(string="Tax Amt", compute="_compute_tax_amt")

    @api.depends('price_unit', 'quantity')
    def _compute_total_contr_amt(self):
        for move in self:
            move.total_contr_amt = 0.0
            if move.quantity and move.price_unit:
                move.total_contr_amt = move.price_unit * move.quantity

    @api.depends('total_contr_amt', 'work_done')
    def _compute_total_work_done(self):
        for move in self:
            move.total_work_done = 0.0
            if move.total_contr_amt and move.work_done:
                move.total_work_done = move.total_contr_amt * (move.work_done / 100)

    @api.depends('total_work_done', 'tax_ids.amount', 'move_id.show_contract_invoice')
    def _compute_tax_amt(self):
        for move in self:
            move.tax_amt = 0.0
            if not move.move_id.show_contract_invoice:
                if move.tax_ids:
                    move.tax_amt = move.total_contr_amt * (move.tax_ids.amount / 100)

                move.price_subtotal = move.quantity * move.price_unit + move.tax_amt
            else:
                if move.tax_ids:
                    move.tax_amt = move.total_work_done * (move.tax_ids.amount / 100)

                move.price_subtotal = move.tax_amt + move.total_work_done

