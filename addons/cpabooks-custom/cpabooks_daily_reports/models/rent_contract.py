from odoo import api, models, fields, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import math
from odoo.exceptions import ValidationError


class RentContract(models.Model):
    _name = 'rent.contract'
    _description = 'Rent Contract Entry Model'
    _rec_name = 'ref'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # Compute methods
    @api.depends('start', 'end')
    def _compute_days(self):
        today = date.today()
        for rec in self:
            if rec.start and rec.end:
                rec.days = (rec.end - today).days + 1
            else:
                rec.days = 0

    @api.depends('start', 'duration')
    def _compute_end(self):
        for rec in self:
            if rec.start and rec.duration:
                rec.end = rec.start + relativedelta(months=rec.duration) - timedelta(days=1)
            elif rec.start:
                rec.end = rec.start + relativedelta(days=364)
            else:
                rec.end = False

    @api.depends('rent_yearly', 'payment_numbers')
    def _compute_rents(self):
        for rec in self:
            # Compute rent_monthly
            rec.rent_monthly = rec.rent_yearly / 12 if rec.rent_yearly else 0

            if rec.rent_yearly and rec.payment_numbers > 0:
                rec.payment_amount = rec.rent_yearly / rec.payment_numbers
            else:
                rec.payment_amount = 0

    @api.depends('partner_id', 'property_location')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id and rec.property_location:
                rec.name = f'{rec.property_location} - {rec.partner_id.name}'
            elif rec.partner_id:
                rec.name = rec.partner_id.name
            elif rec.property_location:
                rec.name = rec.property_location
            else:
                rec.name = rec.ref

    @api.depends('payment_number_line_ids')
    def _get_is_is_payment_number_line_created(self):
        for rec in self:
            if rec.payment_number_line_ids:
                rec.is_payment_number_line_created = True
            else:
                rec.is_payment_number_line_created = False

    ref = fields.Char('Ref', default='NEW', required=True, readonly=True)
    name = fields.Char('Name', compute='_compute_name', store=True)
    partner_id = fields.Many2one('res.partner', 'Land Lord', domain=[('supplier_rank', '>', 0)], tracking=True, required=True)
    property_location = fields.Text('Property Location', tracking=True, required=True)
    duration = fields.Integer('Duration', default=12)
    payment_numbers = fields.Integer('Numbers Of Payments', default=4, required=True)
    payment_amount = fields.Float('Payment Amount',default=0.0, compute=_compute_rents, tracking=True)
    payment_number_line_ids = fields.One2many('payment.number.line', 'contract_id', 'Numbers of Payment and Amount')
    start = fields.Date('Contract Start', tracking=True, required=True)
    end = fields.Date('Contract End', tracking=True, required=True, compute=_compute_end, readonly=False)
    days = fields.Integer('Days', compute='_compute_days', tracking=True)
    rent_yearly = fields.Float('Yearly Rent', tracking=True, required=True)
    deposit = fields.Float('Security Deposit', tracking=True)
    rent_monthly = fields.Float('Monthly Rent', tracking=True, compute=_compute_rents)
    contract_copy = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('progress', 'In Progress'),
    ], 'Contract Copy', default='progress', tracking=True)
    is_payment_number_line_created = fields.Boolean('Is Payment Number Line', default=False, compute=_get_is_is_payment_number_line_created)
    monthly_rent_ids = fields.One2many('rent.monthly.amount.line', 'contract_id', 'Monthly Amount')
    is_account_move = fields.Boolean('Is Used On Bill')

    def name_get(self):
        name = []
        for rec in self:
            name.append((rec.id, '%s - [%s]'%(rec.ref, rec.name)))
        return name

    def _create_payment_number_line_ids(self, contract):
        # Utility function to convert a number to its ordinal representation
        def get_ordinal(n):
            if 10 <= n % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
            return str(n) + suffix

        # Unlink existing payment lines
        if contract.payment_number_line_ids:
            contract.payment_number_line_ids.unlink()

        # Calculate the month duration based on the number of payments
        month_duration = contract.duration // contract.payment_numbers if contract.payment_numbers else 0
        payment_lines = []

        # Iterate through the number of payments
        for i in range(contract.payment_numbers):
            ordinal = get_ordinal(i + 1)

            # Calculate the payment date for each payment
            payment_date = contract.start + relativedelta(months=i * month_duration)

            payment_lines.append((0, 0, {
                'name': f'{ordinal} Payment',
                'contract_id': contract.id,
                'amount': contract.payment_amount,
                'payment_date': payment_date,
            }))

        # Update the contract with new payment lines
        contract.update({'payment_number_line_ids': payment_lines})

        print(contract)

    def _create_monthly_rent_lines(self, contract):
        # Unlink existing monthly rent lines
        if contract.monthly_rent_ids:
            contract.monthly_rent_ids.unlink()

        start_date = contract.start
        end_date = contract.end

        # Calculate total days in the contract period
        total_days_in_contract = (end_date - start_date).days + 1

        # Calculate daily rent based on the exact contract duration
        daily_rent = contract.rent_yearly / total_days_in_contract if total_days_in_contract else 0

        monthly_rents = []
        current_date = start_date

        while current_date <= end_date:
            # Get the last day of the current month
            month_end_day = monthrange(current_date.year, current_date.month)[1]
            month_end = current_date.replace(day=month_end_day)

            if current_date == start_date:
                # Handle first month
                if current_date.day == 1:
                    # Full month rent if contract starts on the first day of the month
                    amount = contract.rent_monthly
                    month_label = f'{current_date.strftime("%B")} {current_date.year}'
                else:
                    # Calculate number of days in the first partial month
                    days_in_first_month = (month_end - current_date).days + 1
                    amount = daily_rent * days_in_first_month
                    month_label = f'{current_date.strftime("%B")} {current_date.year} (Partial)'
            elif month_end >= end_date:
                # Handle last month
                if end_date.day == month_end.day:
                    # Full month rent if contract ends on the last day of the month
                    amount = contract.rent_monthly
                    month_label = f'{current_date.strftime("%B")} {current_date.year}'
                else:
                    # Calculate number of days in the last partial month
                    days_in_last_month = (end_date - current_date).days + 1
                    amount = daily_rent * days_in_last_month
                    month_label = f'{current_date.strftime("%B")} {current_date.year} (Partial)'
            else:
                # Normal full month rent
                amount = contract.rent_monthly
                month_label = f'{current_date.strftime("%B")} {current_date.year}'

            # Add to monthly rent lines
            monthly_rents.append((0, 0, {
                'name': f'{month_label} Rent',
                'contract_id': contract.id,
                'month': current_date.strftime('%B %Y'),
                'amount': math.ceil(amount),
            }))

            # Move to the next month
            current_date = current_date + relativedelta(months=1)
            current_date = current_date.replace(day=1)  # Move to the first day of the next month

        # Ensure the total matches the rent_yearly amount
        total_calculated_rent = sum(rent[2]['amount'] for rent in monthly_rents)

        # Adjust the last month rent to ensure total rent is exactly rent_yearly
        if total_calculated_rent != contract.rent_yearly:
            difference = contract.rent_yearly - total_calculated_rent
            last_month_rent = monthly_rents[-1][2]['amount']
            monthly_rents[-1][2]['amount'] = last_month_rent + difference

        # Create new monthly rent lines
        contract.update({'monthly_rent_ids': monthly_rents})


    @api.model
    def create(self, vals):
        # Automatically assign a sequence number to 'ref'
        if vals.get('ref', _('NEW')) == _('NEW'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('rent.contract') or _('NEW')

        res = super(RentContract, self).create(vals)

        # Create payment number lines and monthly rent lines after creating the contract
        if res.payment_numbers:
            self._create_payment_number_line_ids(res)

        self._create_monthly_rent_lines(res)  # Call the new method to create monthly rent lines

        return res

    def write(self, vals):
        res = super(RentContract, self).write(vals)
        self.change_monthly_rent_ids()

        if any(key in vals for key in ['payment_numbers', 'rent_yearly', 'rent_monthly', 'start', 'end']):
            self._create_payment_number_line_ids(self)
            self._create_monthly_rent_lines(self)


        return res

    def _get_asset(self):
        account_id = self.env['account.move'].search([
            ('company_id', '=', self.env.company.id),
            ('rent_contract_id', '=', self.id)
        ], limit=1, order="id asc")

        assets = account_id.line_ids.mapped("asset_ids").filtered(lambda asset: not asset.name.startswith("VAT"))
        return assets

    def change_monthly_rent_ids(self):
        print('clicked')
        get_all_assets = self.env['account.asset'].sudo().search([])
        for rec in self:
            if rec.is_account_move:
                asset_id = self._get_asset()
                if asset_id in get_all_assets:
                    for record in asset_id.depreciation_move_ids:
                        month = record.date.strftime("%B %Y")
                        monthly_rent_id = rec.monthly_rent_ids.filtered(lambda r: r.month == month)
                        if monthly_rent_id:
                            monthly_rent_id.sudo().write({'cost_amount': record.amount_total})
                else:
                    print('No Asset ID')



    def unlink(self):
        for rec in self:
            if rec.is_account_move:
                raise ValidationError(_("This contract is already linked to an existing bill and cannot be deleted!"))
        return super(RentContract, self).unlink()

    def action_print_pdf(self):
        data = {
            'form': self.read(),  # Read all records
            #'record': self.read(),  # Read all selected records
        }
        return self.env.ref('cpabooks_daily_reports.rent_contract_report').report_action(self, data=data)

class RentContractReport(models.AbstractModel):
    _name = 'report.cpabooks_daily_reports.rent_contract_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = (id['id'] for id in data['form'])
        docs = self.env['rent.contract'].browse(ids)

        return {
            'doc_ids': docids,
            'doc_model': 'rent.contract',
            'docs': docs,
        }


class PaymentNumberLine(models.Model):
    _name = 'payment.number.line'
    _description = 'Payment Number Line'
    _rec_name = 'name'

    name = fields.Char('Name')
    contract_id = fields.Many2one('rent.contract', 'Rent', ondelete='cascade')
    amount = fields.Float('Amount')
    payment_date = fields.Date('Payment Date')



class RentMonthlyAmount(models.Model):
    _name = 'rent.monthly.amount.line'
    _description = 'Rent Monthly Amount Line'
    _rec_name = 'name'

    name = fields.Char('Label')
    contract_id = fields.Many2one('rent.contract', 'Rent' , ondelete='cascade')
    month = fields.Char('Month')
    amount = fields.Integer('Cont. Amount')
    cost_amount = fields.Integer('Cost Amount')

