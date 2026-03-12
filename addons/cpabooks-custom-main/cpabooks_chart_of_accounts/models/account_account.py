import random
import re
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict
import csv
import os
from odoo.exceptions import UserError
from odoo.release import product_name


class Account(models.Model):
    _inherit = 'account.group'

    @api.constrains('code_prefix_start', 'code_prefix_end')
    def _constraint_prefix_overlap(self):
        if self.env.context.get('skip_prefix_constraint'):
            return
        self.env['account.group'].flush()
        query = """
            SELECT other.id FROM account_group this
            JOIN account_group other
              ON char_length(other.code_prefix_start) = char_length(this.code_prefix_start)
             AND other.id != this.id
             AND other.company_id = this.company_id
             AND (
                other.code_prefix_start <= this.code_prefix_start AND this.code_prefix_start <= other.code_prefix_end
                OR
                other.code_prefix_start >= this.code_prefix_start AND this.code_prefix_end >= other.code_prefix_start
            )
            WHERE this.id IN %(ids)s
        """
        self.env.cr.execute(query, {'ids': tuple(self.ids)})
        res = self.env.cr.fetchall()
        if res:
            raise ValidationError(_('Account Groups with the same granularity can\'t overlap'))


class Account(models.Model):
    _inherit = 'account.account'

    get_previous = fields.Boolean('Get Value From Previous', default=True)
    previous = fields.Many2one('account.account', 'Choose Account')
    active = fields.Boolean('Active', default=True)
    qid = fields.Char('QID', reaonly=True)
    is_duplicate = fields.Boolean('Duplicate')
    is_show_code = fields.Boolean('Show-Code')

    _sql_constraints = [
        ('code_company_uniq', 'unique()', 'The code of the account must be unique per company !')
    ]

    @api.model
    def create(self, vals_list):
        res = super(Account, self).create(vals_list)
        user_type_id = self.env['account.account.type'].search([
            ('name', 'ilike', 'Bank and Cash')
        ], limit=1, order='id asc')
        # if res.user_type_id == user_type_id:
        #     self._action_create_journal(res)
        return res

    def write(self, vals):
        res = super(Account, self).write(vals)

        """Update the account journal's name if the user type is 'Bank and Cash'
         when the name field is modified."""

        if 'name' in vals:
            if self.user_type_id and self.user_type_id.name.lower() == 'bank and cash':
                # get account.journal with this coa
                account_journal = self.env['account.journal'].search([
                    ('company_id', '=', self.env.company.id),
                    ('default_account_id', '=', self.id),
                ], limit=1)
                if account_journal:
                    account_journal.write({
                        'name': vals.get('name')
                    })

        # Check if 'user_type_id' is being updated
        if 'user_type_id' in vals:
            user_type_id = self.env['account.account.type'].search([
                ('name', 'ilike', 'Bank and Cash')
            ], limit=1, order='id asc')

            # Loop through all records and trigger action if the user_type_id matches
            # for record in self:
            #     if record.user_type_id == user_type_id:
            #         self._action_create_journal(record)

        return res

    def _action_create_journal(self, coa):
        get_all_journal = self.env['account.journal'].sudo().search([])
        existing_journal = self.env['account.journal'].search([
            '|',
            ('default_account_id', '=', coa.id),
            ('payment_debit_account_id', '=', coa.id),
            ('payment_credit_account_id', '=', coa.id),
            ('company_id', '=', self.env.company.id)
        ], limit=1, order='id asc')

        name = coa.name
        words = name.split()
        code = ''.join((word[0] for word in words))

        journal_type = ''
        if 'bank' in coa.name.lower():
            journal_type = 'bank'
        elif 'cash' in coa.name.lower():
            journal_type = 'cash'
        else:
            journal_type = 'cash'

        if existing_journal in get_all_journal:
            print(f"The account {coa.name} is already linked to the journal: {existing_journal.name}")
            existing_journal.write({
                'name': coa.name,
                'type': journal_type,
                'code': code
            })

        else:
            journal = self.env['account.journal'].create({
                'name': coa.name,
                'type': journal_type,
                'default_account_id': coa.id,
                'code': code,
                'payment_debit_account_id': coa.id,
                'payment_credit_account_id': coa.id,
            })
            print(journal.name)

    def action_create_journals_from_coa(self):
        self.env['account.journal'].create_journals_from_coa()

    # @api.onchange('previous')
    # def get_default_values(self):
    #     for rec in self:
    #         if rec.previous:
    #             code = int(rec.previous.code) + 2
    #             check_code = self.env['account.account'].search([('code', '=', code)])
    #
    #             while check_code:
    #                 code += 1
    #                 check_code = self.env['account.account'].search([('code', '=', code)])
    #
    #             rec.update({
    #                 'name': False,
    #                 'code': code,
    #                 'company_id': rec.previous.company_id.id,
    #                 'user_type_id': rec.previous.user_type_id.id,
    #                 'cash_flow_category': rec.previous.cash_flow_category.id,
    #                 'group_id': rec.previous.group_id.id,
    #                 'tax_ids': rec.previous.tax_ids.ids or False,
    #                 'tag_ids': rec.previous.tag_ids.ids or False,
    #                 'allowed_journal_ids': rec.previous.allowed_journal_ids.ids or False,
    #                 'create_asset': rec.previous.create_asset,
    #                 'asset_model': rec.previous.asset_model.id,
    #                 'reconcile': rec.previous.reconcile,
    #                 'deprecated': rec.previous.deprecated,
    #             })

    @api.onchange('group_id')
    def get_code(self):
        current_company = self.env.company.id
        if self.group_id:
            group_prefix = self.group_id.code_prefix_start
            code_exists = True

            while code_exists:
                random_num = random.randint(100, 999)
                gen_code = f'{group_prefix}-{random_num}'
                # Check if the generated code already exists
                code_exists = self.env['account.account'].search_count([('code', '=', gen_code)]) > 0
                coa = self.env['account.account'].search(
                    [('company_id', '=', current_company), ('group_id', '=', self.group_id.id)], limit=1,
                    order='id desc')

            self.update({
                'code': gen_code,
                'group_id': self.group_id,
                'user_type_id': coa.user_type_id,
            })
            print(gen_code)

    def _load_group(self):
        unallocated = self.env['account.group'].search([('name', '=', 'Unallocated Group')])
        if not unallocated:
            self.env['account.group'].create({'name': 'Unallocated Group'})
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                group = row['group']
                prefix = row['From']
                suffix = row['To']
                # print(f'group: {group}, suffix {suffix}, prefix {prefix}')
                group_id = self.env['account.group'].search([('name', '=', group)])
                if not group_id:
                    self.env['account.group'].with_context(skip_prefix_constraint=True).create({
                        'name': group,
                        'code_prefix_start': prefix,
                        'code_prefix_end': suffix,
                    })
                if group_id:
                    for res in group_id:
                        if res.code_prefix_start and res.code_prefix_end:
                            if prefix not in res.code_prefix_start or suffix not in res.code_prefix_end:
                                res.with_context(skip_prefix_constraint=True).write({
                                    'code_prefix_start': prefix,
                                    'code_prefix_end': suffix,
                                })
                else:
                    pass

        print('Executed _load_group()')
        return True

    def _load_coa(self):
        current_company = self.env.company
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                name = row['account_name']
                revise_name = row['account_name_revise']
                auto_code = row['code_auto']
                user_type = row['type_revise']
                gen_code = f'{auto_code}'
                identity_code = row['code']

                user_type_id = self.env['account.account.type'].search([('name', 'like', user_type)], limit=1)
                coa_all = self.env['account.account'].search(
                    [('name', 'in', (name, revise_name)), ('company_id', '=', current_company.id)])
                coa = self.env['account.account']
                for data in coa_all:
                    if data.identity_code and identity_code == data.identity_code:
                        coa = data
                        break
                    elif not data.identity_code and data.code == identity_code:
                        coa = data
                        break

                # Check if an account with the generated code already exists in the company
                existing_account = self.env['account.account'].search(
                    [('code', '=', gen_code), ('company_id', '=', current_company.id)], limit=1)

                # if existing_account and existing_account.id != coa.id:
                #     # If the code is already taken by a different account, generate a new code or skip
                #     continue  # or handle differently, such as generating a new unique code

                if coa:
                    if coa.code != gen_code:
                        coa.write({
                            'name': revise_name,
                            'code': gen_code,
                            'identity_code': identity_code if (
                                    coa.identity_code != identity_code and identity_code not in (
                                "new", "New", "NEW", False)) else coa.identity_code
                        })
                    else:
                        coa.write({
                            'name': revise_name,
                            'identity_code': identity_code if (
                                    coa.identity_code != identity_code and identity_code not in (
                                "new", "New", "NEW", False)) else coa.identity_code
                        })

                if not coa:
                    reconcile = user_type_id.internal_group in ('asset', 'liability')
                    self.env['account.account'].create({
                        'code': gen_code,
                        'name': revise_name,
                        'user_type_id': user_type_id.id,
                        'reconcile': reconcile,
                        'identity_code': identity_code
                    })
        return True

    def reset_group(self):
        self._load_group()
        unallocated_group_id = self.env['account.group'].search([('name', '=', 'Unallocated Group')], limit=1)
        for rec in self:
            if not rec.group_id:
                rec.write({
                    'group_id': unallocated_group_id.id
                })

    def reset_type(self):
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))

        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                user_type = row['type']
                user_type_revise = row['type_revise']
                # qid = row['qid']
                code = row['code_auto']

                user_type_id = self.env['account.account.type'].search([('name', 'ilike', user_type_revise)], limit=1)

                for rec in self:
                    if rec.code == code:
                        reconcile = user_type_id.internal_group in ('asset', 'liability')
                        rec.update({
                            'user_type_id': user_type_id.id,
                            'reconcile': reconcile
                        })

    def reset_partner(self):
        all_partner_ids = self.env['res.partner'].search([])
        account_receivable = self.env['account.account'].search([('name', '=', 'Accounts Receivable')], limit=1,
                                                                order='id asc')
        account_payable = self.env['account.account'].search([('name', '=', 'Payables')], limit=1, order='id asc')

        # if not account_receivable or not account_payable:
        #     raise UserError('Required accounts (Accounts Receivable or Payables) are not found.')

        for partner_id in all_partner_ids:
            if partner_id.property_account_receivable_id != account_receivable:
                partner_id.property_account_receivable_id = account_receivable.id

            if partner_id.property_account_payable_id != account_payable:
                partner_id.property_account_payable_id = account_payable.id

    def set_pdc(self):
        pdc_customer_account_id = self.env['account.account'].search(
            [('code', 'like', '112-138'), ('name', '=', 'PDC Receivable'), ('company_id', '=', self.env.company.id)],
            limit=1)
        pdc_vendor_account_id = self.env['account.account'].search(
            [('code', 'like', '228-248'), ('name', '=', 'PDC Payable'), ('company_id', '=', self.env.company.id)],
            limit=1)
        settings = self.env['res.config.settings'].search([])
        for setting in settings:
            setting.pdc_customer = pdc_customer_account_id.id
            setting.pdc_vendor = pdc_vendor_account_id.id

    def _action_load_coa(self):
        all_coa_ids = self.env['account.account'].sudo().search([])
        current_company = self.env.company
        csv_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                name = row['account_name']
                revise_name = row['account_name_revise']
                auto_code = row['code_auto']
                user_type = row['type_revise']
                identity_code = row['code']

                user_type_id = self.env['account.account.type'].search([('name', 'like', user_type)], limit=1)
                reconcile = user_type_id.internal_group in ('asset', 'liability')

                get_coa = self.env['account.account'].search([
                    '|', ('name', 'in', (name, revise_name)),
                    ('code', 'in', (auto_code, identity_code)),
                    ('company_id', '=', self.env.company.id)
                ], limit=1)

                if get_coa in all_coa_ids and (
                        get_coa.code != auto_code or get_coa.name != revise_name or get_coa.user_type_id != user_type_id or get_coa.identity_code != identity_code):
                    get_coa.write({
                        'code': auto_code,
                        # 'name': revise_name,
                        'user_type_id': user_type_id.id,
                        'reconcile': reconcile,
                        'identity_code': identity_code
                    })
                if not get_coa in all_coa_ids:
                    self.env['account.account'].create({
                        'code': auto_code,
                        'name': revise_name,
                        'user_type_id': user_type_id.id,
                        'reconcile': reconcile,
                        'identity_code': identity_code
                    })

        return True

    def reset_all(self):
        # self.load_qid()
        # _load_coa
        if self._action_load_coa():
            self.reset_type()
            self.reset_group()
            self.set_pdc()
            self.reset_partner()
            self._create_item()
            self.action_create_far_rules()
            # self.create_deferred_expense_model()
            self.env['ir.sequence'].action_create_sequence()
            # self.env['product.category'].update_product_category_fields()

    @api.model
    def load_coa(self):
        self._load_qid()
        # self._load_coa()
        # self._load_group()

    # @api.constrains('name')
    # def _check_name(self):
    #     for rec in self:
    #         if rec.name:
    #             coa_rec = self.env['account.account'].search(
    #                 [('name', '=ilike', rec.name), ('id', '!=', rec.id),('company_id','=',self.env.company.id)])
    #             if coa_rec:
    #                 raise UserError(_('This Chart Of Account Already exists!'))
    #                 print(coa_rec.name)

    def delete_wizard(self):
        return self.env.ref('cpabooks_chart_of_accounts.coa_create_form_action').read()[0]

    def reset_coa(self):
        return True

    @api.onchange("identity_code")
    def duplicacy_identity_code_chk(self):
        for rec in self:
            if rec.identity_code not in ("new", "New", "NEW", False):
                get_code = self.env['account.account'].sudo().search(
                    [('identity_code', '=', rec.identity_code), ('company_id', '=', self.env.company.id)])
                for line in get_code:
                    raise ValidationError(_("Same Identity Code Found in : %s", line.name))

    def action_create_far_rules(self):
        asset = self.env['account.asset'].search([])
        print([i.name for i in asset])
        expense_id = self.env['account.account'].search([
            ('name', 'ilike', 'Depreciation Costs'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        print(expense_id)
        print(expense_id.name)

        journal_id = self.env['account.journal'].search([
            ('name', 'ilike', 'Miscellaneous Operations'),
        ], limit=1)

        # FAA - Leasehold Improvement
        leasehold = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Leasehold Improvement'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if leasehold:
            leasehold.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Leasehold Improvement')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Leasehold 10 years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': leasehold.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Leasehold 10 years',
                    'method_number': 120,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': leasehold.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            leasehold.asset_model = asset_model.id

        # FAA - Furniture & Fixtures
        furniture_fixtures = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Furniture & Fixtures'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if furniture_fixtures:
            furniture_fixtures.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Furniture & Fixtures')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Furniture & Fustures 5 Years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': furniture_fixtures.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Furniture & Fustures 5 Years',
                    'method_number': 60,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': furniture_fixtures.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            furniture_fixtures.asset_model = asset_model.id

        # FAA - Computer Hardware & Software
        computer_hardware = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Computer Hardware & Software'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if computer_hardware:
            computer_hardware.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Furniture & Fixtures')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Computer Hardware & Fustures 5 Years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': computer_hardware.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,

                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Computer Hardware & Fustures 5 Years',
                    'method_number': 60,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': computer_hardware.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            computer_hardware.asset_model = asset_model.id

        # FAA - Motor Vehicle
        motor = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Motor Vehicle'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if motor:
            motor.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Motor Vehicle')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Motor 10 years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': motor.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Motor 10 years',
                    'method_number': 120,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': motor.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            motor.asset_model = asset_model.id

        # FAA - Equipment & Machineries
        equipment = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Equipment & Machineries'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if equipment:
            equipment.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Equipment & Machineries')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Equipment & Fustures 5 Years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': equipment.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Equipment & Fustures 5 Years',
                    'method_number': 60,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': equipment.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            equipment.asset_model = asset_model.id

        # FAA - Tools & Office Equipment
        tools = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Tools & Office Equipment'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if tools:
            tools.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Tools & Office Equipment')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Tools & Fustures 5 Years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': tools.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Tools & Fustures 5 Years',
                    'method_number': 60,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': tools.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            tools.asset_model = asset_model.id

        # FAA - Building
        building = self.env['account.account'].search([
            ('name', 'ilike', 'FAA - Building'),
            ('user_type_id.name', 'in', ('Fixed Assets', 'Current Assets'))
        ], limit=1)
        if building:
            building.create_asset = 'draft'

            depreciation_account_id = self.env['account.account'].search([
                ('name', 'ilike', 'Acc. Depn. - Building')
            ], limit=1)
            asset_model = self.env['account.asset'].search([
                ('name', 'ilike', 'Building 15 Years')
            ], limit=1)
            if asset_model:
                asset_model.write({
                    'asset_type': 'purchase',
                    'display_account_asset_id': True,
                    'account_depreciation_expense_id': expense_id.id,
                    'state': 'model',
                    'account_asset_id': building.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                })
            else:
                asset_model = self.env['account.asset'].create({
                    'name': 'Building 15 Years',
                    'method_number': 180,
                    'method_period': '1',
                    'prorata': True,
                    'account_asset_id': building.id,
                    'account_depreciation_id': depreciation_account_id.id if depreciation_account_id else False,
                    'account_depreciation_expense_id': expense_id.id,
                    'journal_id': journal_id.id,
                    'asset_type': 'purchase',
                    'state': 'model',
                    'display_account_asset_id': True,
                })
            building.asset_model = asset_model.id

    def action_view_rules(self):
        # Define the action to open the specified tree and form views
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assets',
            'res_model': 'account.asset',
            'view_mode': 'tree,form',  # Show both tree and form views
            'views': [
                (self.env.ref('account_asset.view_account_asset_model_purchase_tree').id, 'tree'),
                (self.env.ref('account_asset.view_account_asset_form').id, 'form'),
            ],
            'target': 'current',
            'context': self.env.context,
            'domain': [('asset_type', '=', 'purchase'), ('state', '=', 'model')],  # Add a domain here if needed #
        }

    def create_category(self):
        parent_category_id = self.env['product.category'].search([
            ('name', 'ilike', 'All')
        ], limit=1, order='id asc')
        category = self.env['product.category'].search([
            ('name', 'ilike', 'COA')
        ], limit=1, order='id asc')

        if not category:
            self.env['product.category'].create({
                'name': 'COA',
                'parent_id': parent_category_id.id,
            })
        return True

    def _create_item(self):
        print('executed _create_item')
        if self.create_category():
            category_id = self.env['product.category'].search([
                ('name', 'ilike', 'COA')
            ], limit=1, order='id asc')

            all_product_ids = self.env['product.template'].search([])

            current_company = self.env.company
            csv_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))
            with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    name = row['account_name']
                    revise_name = row['account_name_revise']
                    auto_code = row['code_auto']
                    user_type = row['type_revise']
                    identity_code = row['code']
                    create_items = row['create_item']
                    link_item_coa = row['link_item_coa']

                    if create_items.lower() == 'yes':
                        income_account_id = self.env['account.account'].search([
                            ('code', '=', auto_code)
                        ], limit=1, order="id asc")

                        # check if product already exists or not

                        product_id = self.env['product.template'].search([
                            '|', ('name', '=', revise_name),
                            ('coa_code', '=', auto_code),
                            ('company_id', '=', self.env.company.id)
                        ], limit=1)

                        if product_id in all_product_ids:
                            product_id.write({
                                'coa_code': auto_code,
                                'property_account_expense_id': income_account_id.id,
                                # 'property_account_income_id': income_account_id.id,
                                'company_id': self.env.company.id,
                                'categ_id': category_id.id,
                                'type': 'product' if user_type == 'Cost of Revenue' else 'service',
                            })

                        else:
                            product_id = self.env['product.template'].create({
                                'name': revise_name,
                                'coa_code': auto_code,
                                'categ_id': category_id.id,
                                'company_id': self.env.company.id,
                                # 'property_account_income_id': income_account_id.id,
                                'property_account_expense_id': income_account_id.id,
                                'type': 'product' if user_type == 'Cost of Revenue' else 'service',
                            })

                        if link_item_coa.lower() == 'yes':
                            product_id.write({
                                'property_account_expense_id': income_account_id.id
                            })
                        else:
                            print(f"link coa is 'no'")
                    else:
                        print(f"Product won't create for '{revise_name}' because create_items: '{create_items}'")

    def action_remove_group(self):
        all_coa = self.env['account.account'].sudo().search([])
        all_coa.group_id = False

    def create_deferred_expense_model(self):
        get_all_coa = self.env['account.account'].sudo().search([])
        get_all_asset = self.env['account.asset'].sudo().search([])

        prepaid_coa_ids = self.env['account.account'].search([
            ('user_type_id.name', 'ilike', 'Prepayments'),
            # ('company_id', '=', self.env.company.id)
        ])
        print(f'pre_coa {[i.name for i in prepaid_coa_ids]}')

        for i in prepaid_coa_ids:
            cleaned_name = re.sub(r'[\s-]*\(?prepaid\)?[\s-]*$', '', i.name, flags=re.IGNORECASE)
            print(f'cleaned {cleaned_name}')
            if cleaned_name != i.name:  # Only proceed if something was removed
                expense_coa_id = self.env['account.account'].search([
                    ('name', 'ilike', cleaned_name),
                    ('user_type_id.name', 'ilike', 'Expenses'),
                    # ('company_id', '=', self.env.company.id)
                ], limit=1)
                print(f'expense {expense_coa_id}')
                journal_id = self.env['account.journal'].search([
                    ('company_id', '=', self.env.company.id),
                    ('name', '=ilike', 'Miscellaneous Operations')
                ], limit=1, order="id asc")
                print(journal_id)

                # Create deferred asset models
                if expense_coa_id in get_all_coa:
                    i.create_asset = 'draft'
                    print(expense_coa_id.name)
                    for months in [12, 6, 3]:
                        model_name = f'{cleaned_name} {months} Months.'
                        model = self.env['account.asset'].search([
                            ('name', 'ilike', model_name),
                            ('company_id', '=', self.env.company.id),
                            ('account_depreciation_id', '=', i.id)
                        ], limit=1)
                        print(f'model {model}')

                        if not model or model not in get_all_asset:
                            model = self.env['account.asset'].create({
                                'name': model_name,
                                'asset_type': 'expense',
                                'state': 'model',
                                'account_depreciation_id': i.id,
                                'account_depreciation_expense_id': expense_coa_id.id,
                                'journal_id': journal_id.id,
                                'prorata': True,
                                'method_number': months,
                                'method_period': '1',
                            })
                        if model in get_all_asset:
                            model.write({
                                'state': 'model',
                                'account_depreciation_id': i.id,
                                'account_depreciation_expense_id': expense_coa_id.id,
                                'journal_id': journal_id.id,
                                'prorata': True,
                            })

                        # Assign asset_model to the first created model (12 months)
                        if months == 12 and not i.asset_model:
                            i.asset_model = model.id

    @api.model
    def default_get(self, fields_list):
        get_last = self.env['account.account'].search([], limit=1, order="id desc")
        self.is_show_code = get_last.is_show_code
        return super(Account, self).default_get(fields_list)

    def action_toggle_code(self):
        get_all_coa_ids = self.env['account.account'].search([])
        for coa in get_all_coa_ids:
            coa.is_show_code = True if not coa.is_show_code else False

    def action_show_code_true(self):
        self.env['account.account'].sudo().search([]).is_show_code = True

    def name_get(self):
        result = []
        for rec in self:
            if rec.is_show_code:
                result.append((rec.id, '%s - %s' % (rec.code, rec.name)))

            else:
                result.append((rec.id, '%s' % (rec.name)))
        return result

    def action_update_selected(self):
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'account_group_type.csv'))

        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                auto_code = row['code_auto']
                user_type = row['type_revise']
                revise_name = row['account_name_revise']
                name = row['account_name']
                identity_code = row['code']

                user_type_id = user_type_id = self.env['account.account.type'].search([
                    ('name', 'like', user_type)
                ], limit=1, order="id asc")
                reconcile = user_type_id.internal_group in ('asset', 'liability')
                for rec in self:
                    if rec.name in (revise_name, name):
                        print(row)
                        rec.write({
                            'code': auto_code,
                            'name': revise_name,
                            'user_type_id': user_type_id.id,
                            'reconcile': reconcile,
                            'identity_code': identity_code
                        })
