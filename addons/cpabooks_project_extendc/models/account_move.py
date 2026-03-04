from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit= "account.move"

    project_id = fields.Many2one('project.project', string='Job Order')

    @api.onchange('project_id')
    def _set_all_analytic_acc(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                line.analytic_account_id=rec.project_id.analytic_account_id.id

class AccountMoveLine(models.Model):
    _inherit= "account.move.line"


    @api.onchange('product_id')
    def _set_analytic_acc(self):
        for rec in self:
            rec.analytic_account_id=rec.move_id.project_id.analytic_account_id.id