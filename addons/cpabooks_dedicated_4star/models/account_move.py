# from addons.sale_subscription_dashboard.controllers.stat_types import currency_normalisation
from odoo import api, models, fields, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    import_purchase_id = fields.Many2one('purchase.order', 'Import Purchase')
    care_of = fields.Char('Care Of')
    dot_matrix_tmpl_id = fields.Many2one('dot.matrix.template' ,'Dot Matrix Template')
    is_print_ageing = fields.Boolean('Print Ageing Report')
    # user_id = fields.Many2one("res.users", "Sales Person")

    @api.onchange('partner_id')
    def action_partner_change_event(self):
        self.ensure_one()
        if self.partner_id:
            additional_info = self.env['res.partner.extra'].sudo().search([
                ('partner_id', '=', self.partner_id.id)
            ], limit=1)
            if not additional_info:
                self.care_of = ''
                self.invoice_payment_term_id = False
                return
            else:
                self.care_of = additional_info.care_of if additional_info.care_of else ''
                self.invoice_payment_term_id = additional_info.payment_terms_id if additional_info.payment_terms_id else False


    @api.model
    def default_get(self, fields_list):
        res = super(AccountMove, self).default_get(fields_list)
        last_move = self.search([],limit=1, order="id desc")
        print(f'context: {self.env.context}')
        if last_move:
            res.update({
                'dot_matrix_tmpl_id': last_move.dot_matrix_tmpl_id.id if last_move.dot_matrix_tmpl_id else False,
                'is_print_ageing': last_move.is_print_ageing
            })
        return res

    def get_month_range(self, year, month):
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        return first_day, last_day

    def action_get_dmt_aging(self):
        """Get aging report for Dot Matrix template"""

        partner = self.partner_id
        today = self.invoice_date or date.today()

        month_summaries = {}
        after_label = ''

        # --- 1. Find the first month’s first day (4 months ago)
        month = today.month - 4
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        first_month_start, _ = self.get_month_range(year, month)

        # --- 2. Calculate "before last 4 months" invoices
        before_invoices = self.env['account.move'].search([
            ('partner_id', '=', partner.id),
            ('invoice_date', '<', first_month_start),
            ('move_type', '=', 'out_invoice'),
            ('state', 'in', ['open', 'posted'])
        ])
        before_total = sum(before_invoices.mapped('amount_residual'))

        before_label = f"Before {first_month_start.strftime('%B %Y')}"
        month_summaries[before_label] = round(before_total, 2)

        # --- 3. Loop over current and previous 4 months
        for i in range(4, -1, -1):  # 4 to 0
            month = today.month - i
            year = today.year

            if month <= 0:
                month += 12
                year -= 1

            first_day, last_day = self.get_month_range(year, month)

            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('invoice_date', '>=', first_day),
                ('invoice_date', '<=', last_day),
                ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['open', 'posted'])
            ])

            total = sum(invoices.mapped('amount_residual'))

            month_label = first_day.strftime('%B %Y')
            month_summaries[month_label] = round(total, 2)

        return month_summaries

    def action_get_net_current_balance(self, net_total_amt):
        symbol = self.env.company.currency_id.symbol
        previous_balance = abs(self.previous_balance)
        net_current_amt = '{0:,.2f}'.format(previous_balance + net_total_amt)
        return_data = ''
        if symbol:
            return_data = f'{symbol} {net_current_amt}'
        else:
            return_data = f'{net_current_amt}'
        return return_data