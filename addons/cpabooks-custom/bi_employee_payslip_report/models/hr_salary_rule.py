from odoo import fields, models,api, _


class HrSalaryRules(models.Model):
    _inherit = 'hr.salary.rule'

    account_debit = fields.Many2one('account.account', 'Debit Account', company_dependent=True,
                                    domain=[('deprecated', '=', False)] ,default=lambda self:self.env['account.account'].search([('name','ilike','Salary & Wages Expenses'),('company_id','=',self.env.company.id)],limit=1))
    account_credit = fields.Many2one('account.account', 'Credit Account', company_dependent=True,
                                     domain=[('deprecated', '=', False)], default=lambda self:self.env['account.account'].search([('name','ilike','Salary & Wages Payable'),('company_id','=',self.env.company.id)],limit=1))

    @api.model
    def action_update_salary_rule_debit_credit(self):
        get_gross_id=self.env['hr.salary.rule'].search([('name', 'ilike', 'Gross%')],limit=1)
        get_net_id=self.env['hr.salary.rule'].search([('name', 'ilike', 'Net%')],limit=1)
        get_all_company = self.env['res.company'].sudo().search([])
        get_debit_credit_line = self.env['ir.property'].sudo().search(
            [('name', 'in', ('account_credit', 'account_debit')),('res_id','not in',('hr.salary.rule,'+str(get_gross_id.id),'hr.salary.rule,'+str(get_net_id.id)))])
        get_debit_credit_line.unlink()
        vals_ir_property = []
        for company in get_all_company:
            get_salary_rules=self.env['hr.salary.rule'].search([('name','not ilike','Gross%'),('name','not ilike','Net%')])
            if get_salary_rules:

                debit_acc=self.env['account.account'].search([('name','ilike','Salary & Wages Expenses'),('company_id','=',company.id)],limit=1)
                credit_acc=self.env['account.account'].search([('name','ilike','Salary & Wages Payable'),('company_id','=',company.id)],limit=1)
                for rule in get_salary_rules:
                        debit_val = {
                            'name': "account_debit",
                            'res_id': 'hr.salary.rule,' + str(rule.id),
                            'company_id': company.id,
                            'fields_id': self.env['ir.model.fields'].search(
                                [('name', '=', 'account_debit'),
                                 ('model', '=', 'hr.salary.rule')]).id,
                            'value_reference': 'account.account,' + str(debit_acc.id),
                            'type': 'many2one'
                        }
                        vals_ir_property.append(debit_val)
                        credit_val = {
                            'name': "account_credit",
                            'res_id': 'hr.salary.rule,' + str(rule.id),
                            'company_id': company.id,
                            'fields_id': self.env['ir.model.fields'].search(
                                [('name', '=', 'account_credit'),
                                 ('model', '=', 'hr.salary.rule')]).id,
                            'value_reference': 'account.account,' + str(credit_acc.id),
                            'type': 'many2one'
                        }
                        vals_ir_property.append(credit_val)
        self.env['ir.property'].sudo().create(vals_ir_property)
                    # rule.account_debit=debit_acc.id
                    # rule.account_credit=credit_acc.id

    @api.model
    def create_salary_journal(self):
        get_all_company = self.env['res.company'].sudo().search([])
        val_list=[]
        for company in get_all_company:
            get_salary_journal=self.env['account.journal'].sudo().search([('name','=','Salary Journal'),('company_id','=',company.id)])
            if not get_salary_journal:
                vals={
                    'code':'SJ',
                    'name':'Salary Journal',
                    'company_id': company.id,
                    'type': 'general',
                    # 'type_control_ids':self.env['account.account.type'].sudo().search([('name','in',('Current Assets','Current Liabilities'))]).ids,
                    # 'account_control_ids': self.env['account.account'].sudo().search([('name','in',('Salaries Payable','Salaries & allowances')),('company_id','=',company.id)]).ids,
                    'type_control_ids':[],
                    'account_control_ids':[],
                    'default_debit_account_id': self.env['account.account'].sudo().search([('name','ilike','Salary & Wages Payable'),('company_id','=',company.id)],limit=1).id,
                    'default_credit_account_id': self.env['account.account'].sudo().search(
                        [('name', 'ilike', 'Salary & Wages Expenses'), ('company_id', '=', company.id)],limit=1).id,
                }
                val_list.append(vals)
            else:
                for rec in get_salary_journal:
                    rec.code='SJ'
                    rec.type='general'
                    rec.type_control_ids=[(5,0,0)]
                    rec.account_control_ids=[(5,0,0)]
                    rec.default_debit_account_id=self.env['account.account'].sudo().search([('name','ilike','Salary & Wages Payable'),('company_id','=',company.id)],limit=1).id
                    rec.default_credit_account_id=self.env['account.account'].sudo().search(
                        [('name', 'ilike', 'Salary & Wages Expenses'), ('company_id', '=', company.id)],limit=1).id
        if len(val_list)>0:
            self.env['account.journal'].sudo().create(val_list)

        get_salary_structure_journal_ids = self.env['ir.property'].sudo().search(
            [('name', '=', 'journal_id'),('res_id','ilike','hr.payroll.structure%')])
        get_salary_structure_journal_ids.unlink()
        vals_ir_property=[]
        for com in get_all_company:
            get_salary_structure = self.env['hr.payroll.structure'].sudo().search([])
            for rec in get_salary_structure:
                val = {
                    'name': "journal_id",
                    'res_id': 'hr.payroll.structure,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'journal_id'),
                         ('model', '=', 'hr.payroll.structure')]).id,
                    'value_reference': 'account.journal,' + str(self.env['account.journal'].sudo().search([('company_id','=',com.id),('name','=','Salary Journal')]).id),
                    'type': 'many2one'
                }
                vals_ir_property.append(val)
        self.env['ir.property'].sudo().create(vals_ir_property)

