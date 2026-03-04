from email.policy import default

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import date

STATE = [
    ('todo', 'TO DO'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('hold', 'Hold')
]

class ProjectTask(models.Model):
    _inherit = 'project.task'

    state = fields.Selection(STATE, 'State', default='todo')
    scope_id = fields.Many2one('project.task.scope', 'Scope Group')
    remarks = fields.Text('Remarks', tracking=True)
    last_action = fields.Text('Last Action', tracking=True)
    date_start = fields.Date('Start Date', default=fields.Date.today)
    date_end = fields.Date('End Date')
    priority_id = fields.Many2one('project.task.priority', 'Priority')
    frequency_id = fields.Many2one('project.task.frequency', 'Freq')
    task_seq = fields.Char('TID')
    is_group = fields.Boolean('Is Group', default=0)
    task_group_id = fields.Many2one('project.task', 'Task Group', domain=[('is_group', '=', True)], context={'is_group': True})
    amount = fields.Float('Cont. Amount')
    period = fields.Selection([
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
        ('once', 'Once')
    ], 'Period')
    amount_per_year = fields.Float('Amount Per Year', compute='_compute_amount_per_year')
    amount_paid = fields.Float('Paid Amount')
    amount_due = fields.Float('Due Amount', compute="_compute_due_amount")
    crm_id = fields.Many2one('crm.lead', 'CRM', compute='_get_crm_id', store=True)
    aging_days = fields.Integer('Aging Days', compute="_compute_aging_days")
    check_fsm = fields.Boolean('Check FSM')

    @api.onchange('state')
    def add_date_end(self):
        self.ensure_one()
        if self.date_end:
            return
        if self.state == 'done':
            self.date_end = date.today()

    def action_reset_name(self):
        """Launch task update wizard to update selected tasks name"""
        return {
            'name': 'Update Tasks Name',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'res_model': 'task.update.wizard',
            'context': {
                'active_ids': self.ids
            },
            'view_mode': 'form',
            'target': 'new'
        }

    @api.depends('date_start')
    def _compute_aging_days(self):
        for rec in self:
            today = date.today()  # Note: date.today() is a method, not datetime.date()
            if rec.date_start:
                delta = today - rec.date_start
                rec.aging_days = delta.days
            else:
                rec.aging_days = 0
    # task_sr_id = fields.Integer('Task ID', compute='_compute_task_sr_id')
    #
    # @api.depends('project_id')
    # def _compute_task_sr_id(self):
    #     for rec in self:
    #         if rec.project_id:
    #             prev_tasks = self.env['project.task'].search([
    #                 ('project_id', '=', rec.project_id.id),
    #                 ('company_id', '=', self.env.company.id)
    #             ],order='id asc')
    #             print(prev_tasks)
    #             rec.task_sr_id = 1

    def action_reset_tid(self):
        all_tasks = self.search([], order="create_date")
        print(len(all_tasks))
        seq = 1
        for task in all_tasks:
            create_date = fields.Datetime.from_string(task.create_date)
            year = create_date.year
            sequence = f'TID-{year}-{seq:04d}'
            task.task_seq = sequence
            seq += 1
        ir_seq = self.env['ir.sequence'].sudo().search([
            ('code', '=', 'sequence_for_task')
        ], limit=1)
        if ir_seq:
            ir_seq.number_next_actual = seq

    @api.depends('project_id')
    def _get_crm_id(self):
        for rec in self:
            if rec.project_id:
                rec.crm_id = rec.project_id.crm_id
            else:
                rec.crm_id = False

    @api.depends('amount', 'amount_paid')
    def _compute_due_amount(self):
        for rec in self:
            rec.amount_due = rec.amount - rec.amount_paid

    @api.depends('amount', 'period')
    def _compute_amount_per_year(self):
        for rec in self:
            amount_per_year = 0.0
            if rec.amount and rec.period:
                mul = 0
                if rec.period == 'month':
                    mul = 12
                elif rec.period == 'quarter':
                    mul = 4
                elif rec.period == 'year':
                    mul = 1
                try:
                    amount_per_year = rec.amount * mul
                except Exception as e:
                    print(e)
            rec.amount_per_year = amount_per_year

    def _update_name(self):
        print(self.name)
        name_lst = self.name
        if ' - ' in name_lst:
            name_lst = self.name.split(' - ', 1)[1]
        self.name = f'{self.project_id.name} - {name_lst}' if self.project_id else name_lst

    def action_update_name(self):
        self._update_name()

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        res._update_name()
        res.task_seq = self.env['ir.sequence'].next_by_code('sequence_for_task')
        return  res

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if vals.get('project_id'):
            self._update_name()
        return res


class ProjectTaskFrequency(models.Model):
    _name = 'project.task.frequency'
    _description = 'Project Task Frequency'
    _rec_name = 'name'

    name = fields.Char('Name')

    @api.model
    def action_create_default_frequency(self):
        freq_lst = [
            'Daily',
            'Monthly',
            'Quarterly',
            'Yearly'
        ]
        for lst in freq_lst:
            exists = self.search([
                ('name', '=ilike', lst)
            ], limit=1)
            if not exists:
                self.create({'name': lst})
