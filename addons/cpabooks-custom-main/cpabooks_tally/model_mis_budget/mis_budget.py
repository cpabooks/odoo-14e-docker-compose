from vobject.base import logical_lines_re

from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

MONTHS = [
    ('jan', 'January'),
    ('feb', 'February'),
    ('mar', 'March'),
    ('apr', 'April'),
    ('may', 'May'),
    ('jun', 'June'),
    ('jul', 'July'),
    ('aug', 'August'),
    ('sep', 'September'),
    ('oct', 'October'),
    ('nov', 'November'),
    ('dec', 'December')
]


class MisBudget(models.Model):
    _name = 'mis.budget'
    _description = 'MIS Budget'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    is_ledger_loaded = fields.Boolean('Ledger loaded', compute='_check_ledger_loaded')

    income_budget_line_ids = fields.One2many('income.mis.budget.line', 'mis_id', 'Income Budget Line')
    is_repeat_income = fields.Boolean('Repeat Lines (Income)')
    expense_budget_line_ids = fields.One2many('expense.mis.budget.line', 'mis_id', 'Expense Budget Line')
    is_repeat_expense = fields.Boolean('Repeat Lines (Expense)')
    customer_line_ids = fields.One2many('budget.customer.line', 'mis_id', 'Customers')
    is_repeat_customer = fields.Boolean('Repeat Lines (Customer)')
    vendor_line_ids = fields.One2many('budget.vendor.line', 'mis_id', 'Vendors')
    is_repeat_vendor = fields.Boolean('Repeat Lines (Vendor)')

    forecast_line = fields.One2many('forecast.line.income', 'mis_id', 'Forecast')
    forecast_line_expense = fields.One2many('forecast.line.expense', 'mis_id', 'Forecast Expense')
    forecast_line_vendor = fields.One2many('forecast.line.vendor', 'mis_id', 'Forecast Vendor')
    forecast_line_customer = fields.One2many('forecast.line.customer', 'mis_id', 'Customer')
    forecast_mon_cy = fields.Selection(MONTHS, 'Month CY', default='jan')
    forecast_mon_cyp = fields.Selection(MONTHS, 'Month CYP', default='jan')

    @api.model
    def create(self, vals):
        """Create income, expense, partner and vendor lines with tow values"""
        res = super(MisBudget, self).create(vals)
        # Create income budget line
        if not res.income_budget_line_ids:
            income_budget_line = self.env['income.mis.budget.line']
            income_accounts = self.env['account.account'].search([
                ('user_type_id.name', 'ilike', 'income'),
                ('company_id', '=', self.env.company.id)
            ], limit=2)
            if income_accounts:
                for account in income_accounts:
                    income_budget_line.create({
                        'actual_cy_account': account.id,
                        'mis_id': res.id
                    })
                    _logger.info(f"Income Budget Line created for {account.name}")
            else:
                _logger.warning(f"No Income Accounts found on Chart Of Accounts")
        # Create Expense budget line
        if not res.expense_budget_line_ids:
            expense_budget_line = self.env['expense.mis.budget.line']
            expense_accounts = self.env['account.account'].search([
                ('user_type_id', 'ilike', 'expense'),
                ('company_id', '=', self.env.company.id)
            ], limit=2)
            if expense_accounts:
                for account in expense_accounts:
                    expense_budget_line.create({
                        'actual_cy_account': account.id,
                        'mis_id': res.id
                    })
                    _logger.info(f"Expense Budget Line created for {account.name}")
            else:
                _logger.warning(f"No Expense Account found")
        # Create Customer
        if not res.customer_line_ids:
            customer_line = self.env['budget.customer.line']
            customer_ids = self.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('company_id', '=', self.env.company.id)
            ], limit=2)
            if customer_ids:
                for customer in customer_ids:
                    customer_line.create({
                        'actual_cy_partner': customer.id,
                        'mis_id': res.id
                    })
                    _logger.info(f"Budget Customer Line created for {customer.name}")
            else:
                _logger.warning(f"Customer not found")
        # Create vendor
        if not res.vendor_line_ids:
            vendor_line = self.env['budget.vendor.line']
            vendor_ids = self.env['res.partner'].search([
                ('supplier_rank', '>', 0),
                ('company_id', '=', self.env.company.id)
            ], limit=2)
            if vendor_ids:
                for vendor in vendor_ids:
                    vendor_line.create({
                        'actual_cy_partner': vendor.id,
                        'mis_id': res.id
                    })
                    _logger.info(f"Budget Vendor Line Created for {vendor.name}")
            else:
                _logger.warning(f"Vendor not found")
        return res

    def load_ledgers(self):
        """Create income, expense, partner, and vendor lines"""
        for rec in self:
            if not rec.is_ledger_loaded:
                # Create Income Budget Line
                income_accounts = self.env['account.account'].search([
                    ('user_type_id.name', 'ilike', 'income'),
                    ('company_id', '=', self.env.company.id)
                ])
                existing_income_accounts = rec.income_budget_line_ids.mapped('actual_cy_account.id')

                for account in income_accounts:
                    if account.id not in existing_income_accounts:
                        self.env['income.mis.budget.line'].create({
                            'actual_cy_account': account.id,
                            'mis_id': rec.id
                        })
                        _logger.info(f"Income Budget Line created for {account.name}")

                # Create Expense Budget Line
                expense_accounts = self.env['account.account'].search([
                    ('user_type_id.name', 'ilike', 'expense'),
                    ('company_id', '=', self.env.company.id)
                ])
                existing_expense_accounts = rec.expense_budget_line_ids.mapped('actual_cy_account.id')

                for account in expense_accounts:
                    if account.id not in existing_expense_accounts:
                        self.env['expense.mis.budget.line'].create({
                            'actual_cy_account': account.id,
                            'mis_id': rec.id
                        })
                        _logger.info(f"Expense Budget Line created for {account.name}")

                # Create Customer Budget Line
                customers = self.env['res.partner'].search([
                    ('customer_rank', '>', 0),
                    ('company_id', '=', self.env.company.id)
                ])
                existing_customers = rec.customer_line_ids.mapped('actual_cy_partner.id')

                for customer in customers:
                    if customer.id not in existing_customers:
                        self.env['budget.customer.line'].create({
                            'actual_cy_partner': customer.id,
                            'mis_id': rec.id
                        })
                        _logger.info(f"Budget Customer Line created for {customer.name}")

                # Create Vendor Budget Line
                vendors = self.env['res.partner'].search([
                    ('supplier_rank', '>', 0),
                    ('company_id', '=', self.env.company.id)
                ])
                existing_vendors = rec.vendor_line_ids.mapped('actual_cy_partner.id')

                for vendor in vendors:
                    if vendor.id not in existing_vendors:
                        self.env['budget.vendor.line'].create({
                            'actual_cy_partner': vendor.id,
                            'mis_id': rec.id
                        })
                        _logger.info(f"Budget Vendor Line Created for {vendor.name}")

    def clean_ledgers(self):
        for rec in self:
            if rec.is_ledger_loaded:
                rec.income_budget_line_ids.unlink()
                rec.expense_budget_line_ids.unlink()
                rec.customer_line_ids.unlink()
                rec.vendor_line_ids.unlink()

    def _check_ledger_loaded(self):
        """Check if all ledgers are loaded or not"""
        for rec in self:
            loaded = True  # Assume loaded to be true initially

            # Check income line
            income_accounts = self.env['account.account'].search([
                ('user_type_id.name', 'ilike', 'income'),
                ('company_id', '=', self.env.company.id)
            ])
            if income_accounts and len(rec.income_budget_line_ids) < len(income_accounts):
                loaded = False

            # Check expense line
            expense_accounts = self.env['account.account'].search([
                ('user_type_id', 'ilike', 'expense'),
                ('company_id', '=', self.env.company.id)
            ])
            if expense_accounts and len(rec.expense_budget_line_ids) < len(expense_accounts):
                loaded = False

            # Check customer line
            customer_ids = self.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('company_id', '=', self.env.company.id)
            ])
            if customer_ids and len(rec.customer_line_ids) < len(customer_ids):
                loaded = False

            # Check Vendors
            vendor_ids = self.env['res.partner'].search([
                ('supplier_rank', '>', 0),
                ('company_id', '=', self.env.company.id)
            ])
            if vendor_ids and len(rec.vendor_line_ids) < len(vendor_ids):
                loaded = False

            rec.is_ledger_loaded = loaded

    def _get_col_name(self, type, val):
        col_name = ''
        if type == 'cy':
            col_name = "actual_%s_%s" % (type, val)
        if type == 'cyp':
            col_name = "payment_%s_%s" % (type, val)
        return col_name

    def _set_forecast_income(self, col_name):
        all_income_lines = self.env['income.mis.budget.line'].search([])
        for line in all_income_lines:
            account_id = line.actual_cy_account
            amount = getattr(line, col_name, 0)
            if amount >= 1 and account_id:
                forecast_income_id = self.env['forecast.line.income'].search([
                    ('mis_id', '=', self.ids[0]),
                    ('income_account_id', '=', account_id.id)
                ], limit=1)
                if forecast_income_id:
                    if 'payment_cyp' in col_name:
                        forecast_income_id.income_cyp = amount
                    elif 'actual_cy' in col_name:
                        forecast_income_id.write({
                            'income_cy': amount
                        })
                    else:
                        print('error')

    def _set_forecast_expense(self, col_name):
        all_expense_line = self.env['expense.mis.budget.line'].search([])
        for line in all_expense_line:
            account_id = line.actual_cy_account
            amount = getattr(line, col_name, 0)
            if amount >= 1 and account_id:
                forecast_expense_id = self.env['forecast.line.expense'].search([
                    ('mis_id', '=', self.ids[0]),
                    ('expense_account_id', '=', account_id.id)
                ], limit=1)
                if forecast_expense_id:
                    if 'payment_cyp' in col_name:
                        forecast_expense_id.expense_cyp = amount
                    elif 'actual_cy' in col_name:
                        forecast_expense_id.expense_cy = amount

    def _set_forecast_partner(self, col_name, forecast_type):
        budget_lines = None
        if forecast_type == 'customer':
            budget_lines = self.env['budget.customer.line'].search([])
        elif forecast_type == 'vendor':
            budget_lines = self.env['budget.vendor.line'].search([])

        if budget_lines:
            for line in budget_lines:
                partner_id = line.actual_cy_partner
                amount = getattr(line, col_name, 0)
                if partner_id and amount >= 1:
                    forecast_id = None
                    if forecast_type == 'customer':
                        forecast_id = self.env['forecast.line.customer'].search([
                            ('mis_id', '=', self.ids[0]),
                            ('partner_id', '=', partner_id.id)
                        ], limit=1)

                    elif forecast_type == 'vendor':
                        forecast_id = self.env['forecast.line.vendor'].search([
                            ('mis_id', '=', self.ids[0]),
                            ('partner_id', '=', partner_id.id)
                        ], limit=1)
                    if forecast_id:
                        if 'actual_cy' in col_name:
                            forecast_id.cy = amount
                        elif 'payment_cyp' in col_name:
                            forecast_id.cyp = amount


    @api.onchange('forecast_mon_cy')
    def get_month_cy(self):
        col_name = self._get_col_name('cy', self.forecast_mon_cy)
        self._set_forecast_income(col_name)
        self._set_forecast_expense(col_name)
        self._set_forecast_partner(col_name, 'customer')
        self._set_forecast_partner(col_name, 'vendor')


    @api.onchange('forecast_mon_cyp')
    def get_month_cyp(self):
        col_name = self._get_col_name('cyp', self.forecast_mon_cyp)
        self._set_forecast_income(col_name)
        self._set_forecast_expense(col_name)
        self._set_forecast_partner(col_name, 'customer')
        self._set_forecast_partner(col_name, 'vendor')



    def action_load_forecast_line(self):
        """Insert value in forecasts (income, expenses, customer and vendors)"""
        self.ensure_one()
        self.forecast_line = False
        self.forecast_line_expense = False
        self.forecast_line_vendor = False
        self.forecast_line_customer = False

        # Insert value in forecast income
        for line in self.income_budget_line_ids.mapped('actual_cy_account'):
            self.forecast_line = [(0, 0, {'income_account_id': line.id})]

        # Insert value in forecast expenses
        for line in self.expense_budget_line_ids.mapped('actual_cy_account'):
            self.forecast_line_expense = [(0, 0, {'expense_account_id': line.id})]

        # Insert value in forecast customer
        for line in self.customer_line_ids.mapped('actual_cy_partner'):
            self.forecast_line_customer = [(0, 0, {'partner_id': line.id})]

        # Insert value in forecast customer
        for line in self.vendor_line_ids.mapped('actual_cy_partner'):
            self.forecast_line_vendor = [(0, 0, {'partner_id': line.id})]
