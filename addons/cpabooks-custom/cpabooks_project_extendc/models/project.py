from odoo import api, models, fields, _


class Project(models.Model):
    _inherit = 'project.project'


    def _compute_invoices(self):
        for rec in self:
            invoices = self.env['account.move'].search_count([('project_id','=',rec.id),('move_type', '=', 'out_invoice')])
            rec.invoices_count = invoices

    def _compute_bills(self):
        for rec in self:
            bills = self.env['account.move'].search_count([('project_id','=',rec.id),('move_type', '=', 'in_invoice')])
            rec.bills_count = bills

    def _get_invoices(self):
        for rec in self:
            rec.invoice_ids = [(6, 0, self.env['account.move'].search(
                [('project_id', '=', rec.id), ('move_type', '=', 'out_invoice')]).ids)]

    count_analytic_amount = fields.Float('Profit', compute='_compute_analytic')
    expenses = fields.Float('Expenses', compute='_compute_expenses') #compute='_compute_expenses'
    sales = fields.Float('Sales', compute='_compute_sales') #compute='_compute_sales'
    invoices_count = fields.Integer('Invoices', compute=_compute_invoices)
    bills_count = fields.Integer('Invoices', compute=_compute_bills)
    invoice_ids = fields.Many2many(
        'account.move',
        string='Invoices', compute=_get_invoices
    )
    location_id = fields.Many2one('project.location', 'Location')
    project_pid = fields.Char('PID')
    is_group = fields.Boolean('Group', default=0)
    project_group_id = fields.Many2one('project.project', 'Project Group', domain="[('is_group', '=', True)]", context="{'is_group': True}")
    contract_amount = fields.Float('Contract Amount', compute="_compute_contract_amount")
    amount_per_year = fields.Float('Amount Per Year', compute='_compute_contract_amount')
    crm_id = fields.Many2one('crm.lead', 'CRM', search=True)
    total_task_count = fields.Integer('Tasks', compute='_compute_total_task_count')

    def _compute_total_task_count(self):
        task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', '&', ('stage_id.is_closed', '=', False), ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.total_task_count = result.get(project.id, 0)

    def action_show_task_extend(self):
        self.ensure_one()

        return {
            'name': f'Tasks - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,pivot',
            'domain': [
                ('project_id', '=', self.id),
                '|',
                '&', ('stage_id.is_closed', '=', False),
                ('stage_id.fold', '=', False),
                ('stage_id', '=', False)
            ],
            'context': {
                'default_project_id': self.id,
                'search_default_group_by_user': 1,
                'search_default_project_id': self.id,
                'pivot_row_groupby': ['user_id'],
                'force_update_context': True,  # Force context update
            },
            'target': 'current',
        }

    # def action_show_task_extend(self):
    #     self.ensure_one()  # Ensure single record
    #
    #     # Get tasks with your criteria
    #     tasks = self.env['project.task'].search([
    #         ('project_id', 'in', self.ids),
    #         '|',
    #         '&', ('stage_id.is_closed', '=', False),
    #         ('stage_id.fold', '=', False),
    #         ('stage_id', '=', False)
    #     ])
    #
    #     # Prepare view IDs explicitly to ensure proper context application
    #     kanban_view = self.env.ref('project.view_task_kanban').id
    #     tree_view = self.env.ref('project.view_task_tree2').id
    #     form_view = self.env.ref('project.view_task_form2').id
    #     # pivot_view = self.env.ref('project.view_task_pivot').id
    #
    #     action = {
    #         'name': f'Tasks - {self.name}',
    #         'type': 'ir.actions.act_window',
    #         'model': 'ir.actions.act_window',
    #         'res_model': 'project.task',
    #         'view_mode': 'kanban,tree,form,pivot',
    #         # 'views': [
    #         #     (kanban_view, 'kanban'),
    #         #     (tree_view, 'tree'),
    #         #     (form_view, 'form'),
    #         #     # (pivot_view, 'pivot')
    #         # ],
    #         'domain': [('id', 'in', tasks.ids)],
    #         'context': {
    #             'default_project_id': self.id,
    #             'search_default_group_by_user': 1,
    #             'search_default_project_id': self.id,
    #             # Force context update
    #             'force_update_context': True,
    #             # Clear any possible conflicting context
    #             'group_by': None,
    #             'pivot_row_groupby': ['user_id'],
    #         },
    #         'target': 'current',
    #     }
    #     print(action)
    #     return action

        # return {
        #     'name': f'Tasks - {self.name}',
        #     'type': 'ir.actions.act_window',
        #     'model': 'ir.actions.act_window',
        #     'res_model': 'project.task',
        #     'view_mode': 'kanban,tree,form,pivot',
        #     'views': [
        #         (kanban_view, 'kanban'),
        #         (tree_view, 'tree'),
        #         (form_view, 'form'),
        #         # (pivot_view, 'pivot')
        #     ],
        #     'domain': [('id', 'in', tasks.ids)],
        #     'context': {
        #         'default_project_id': self.ids[0],
        #         'search_default_group_by_user': 1,
        #         'search_default_project_id': self.id,
        #         # Force context update
        #         'force_update_context': True,
        #         # Clear any possible conflicting context
        #         'group_by': None,
        #         'pivot_row_groupby': ['user_id'],
        #     },
        #     'target': 'current',
        # }


    def action_reset_pid(self):
        all_projects = self.search([], order="create_date")
        seq = 1
        for project in all_projects:
            create_date = fields.Datetime.from_string(project.create_date)
            year = create_date.year
            sequence = f'PID-{year}-{seq:04d}'
            project.project_pid = sequence
            seq += 1
        ir_seq = self.env['ir.sequence'].sudo().search([
            ('code', '=', 'project.sequence')
        ], limit=1)
        if ir_seq:
            ir_seq.number_next_actual = seq

    def _compute_contract_amount(self):
        for rec in self:
            task_ids = self.env['project.task'].search([
                ('project_id', '=', rec.id)
            ])
            amount = 0
            amount_year = 0.0
            for task_id in task_ids:
                amount += task_id.amount
                amount_year += task_id.amount_per_year
            rec.contract_amount = amount
            rec.amount_per_year = amount_year

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        if not res.project_pid:
            res.project_pid = self.env['ir.sequence'].next_by_code('project.sequence')
        return res

    def _compute_expenses(self):
        for rec in self:
            # if rec.count_analytic_amount < 0.00:
            #     rec.expenses = rec.count_analytic_amount
            # elif rec.count_analytic_amount >= 0.00:
            #     rec.expenses = 0.00
            count = self.env['account.analytic.line'].search([('account_id', '=', rec.analytic_account_id.id)])
            rec.expenses = count.account_id.debit


    def _compute_sales(self):
        for rec in self:
            # if rec.count_analytic_amount > 0.00:
            #     rec.sales = rec.count_analytic_amount
            # elif rec.count_analytic_amount <= 0.00:
            #     rec.sales = 0.00
            count = self.env['account.analytic.line'].search([('account_id', '=', rec.analytic_account_id.id)])
            rec.sales = count.account_id.credit


    def _compute_analytic(self):
        for rec in self:
            count = self.env['account.analytic.line'].search([('account_id', '=', rec.analytic_account_id.id)])
            rec.count_analytic_amount = sum(amount.amount for amount in count)


    def action_analytic(self):
        domain = [('account_id', '=', self.analytic_account_id.id)]
        return {
            'name': "Cost Center/Analytics",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'account.analytic.line',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'domain': domain,
            'context': {'group_by': 'general_account_id'},
        }

    def action_invoices(self):
        domain = [('project_id','=',self.id),('move_type', '=', 'out_invoice')]
        return {
            'name': "Invoices",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': domain,
            'target':'current'
        }

    def action_bills(self):
        domain = [('project_id','=',self.id),('move_type', '=', 'in_invoice')]
        return {
            'name': "Invoices",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': domain,
            'target':'current'
        }

    @api.model
    def default_get(self, fields):
        vals = super(Project, self).default_get(fields)
        vals.update({
            'allow_billable': True
        })
        return vals

