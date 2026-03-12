import babel.dates
from dateutil.relativedelta import relativedelta
import itertools
import json

from odoo.addons.sale_timesheet.models.project_overview import _to_action_data
from odoo import fields, _, models, api
from odoo.osv import expression
from odoo.tools import float_round
from odoo.tools.misc import get_lang

DEFAULT_MONTH_RANGE = 3


class Project(models.Model):
    _inherit = 'project.project'

    invoice_ids = fields.Many2many('account.move', string="Invoices", compute="_get_related_invoices")

    @api.depends('company_id')
    def _get_related_invoices(self):
        if self.ids:
            get_invoices = self.env['account.move'].sudo().search([('project_id', '=', self.ids[0])])
            self.invoice_ids = [(6, 0, get_invoices.ids)]
        else:
            self.invoice_ids = None

    def _plan_get_stat_button(self):
        stat_buttons = []
        num_projects = len(self)
        if num_projects == 1:
            action_data = _to_action_data('project.project', res_id=self.id,
                                          views=[[self.env.ref('project.edit_project').id, 'form']])
        else:
            action_data = _to_action_data(action=self.env.ref('project.open_view_project_all_config'),
                                          domain=[('id', 'in', self.ids)])

        stat_buttons.append({
            'name': _('Project') if num_projects == 1 else _('Projects'),
            'count': num_projects,
            'icon': 'fa fa-puzzle-piece',
            'action': action_data
        })

        # if only one project, add it in the context as default value
        tasks_domain = [('project_id', 'in', self.ids)]
        tasks_context = self.env.context.copy()
        tasks_context.pop('search_default_name', False)
        late_tasks_domain = [('project_id', 'in', self.ids),
                             ('date_deadline', '<', fields.Date.to_string(fields.Date.today())),
                             ('date_end', '=', False)]
        overtime_tasks_domain = [('project_id', 'in', self.ids), ('overtime', '>', 0), ('planned_hours', '>', 0)]

        # filter out all the projects that have no tasks
        task_projects_ids = self.env['project.task'].read_group([('project_id', 'in', self.ids)], ['project_id'],
                                                                ['project_id'])
        task_projects_ids = [p['project_id'][0] for p in task_projects_ids]

        if len(task_projects_ids) == 1:
            tasks_context = {**tasks_context, 'default_project_id': task_projects_ids[0]}
        stat_buttons.append({
            'name': _('Tasks'),
            'count': sum(self.mapped('task_count')),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=tasks_domain,
                context=tasks_context
            )
        })
        stat_buttons.append({
            'name': [_("Tasks"), _("Late")],
            'count': self.env['project.task'].search_count(late_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=late_tasks_domain,
                context=tasks_context,
            ),
        })
        stat_buttons.append({
            'name': [_("Tasks"), _("in Overtime")],
            'count': self.env['project.task'].search_count(overtime_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=overtime_tasks_domain,
                context=tasks_context,
            ),
        })

        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            # read all the sale orders linked to the projects' tasks
            # task_so_ids = self.env['project.task'].search_read([
            #     ('project_id', 'in', self.ids), ('sale_order_id', '!=', False)
            # ], ['sale_order_id'])
            # task_so_ids = [o['sale_order_id'][0] for o in task_so_ids]
            task_so_ids = self.env['sale.order'].search([('project_id', 'in', self.ids)])

            sale_orders = self.mapped('sale_line_id.order_id') | self.env['sale.order'].browse(task_so_ids.ids)
            if sale_orders:
                stat_buttons.append({
                    'name': _('Sales Orders'),
                    'count': len(sale_orders),
                    'icon': 'fa fa-dollar',
                    'action': _to_action_data(
                        action=self.env.ref('sale.action_orders'),
                        domain=[('id', 'in', sale_orders.ids)],
                        context={'create': False, 'edit': False, 'delete': False}
                    )
                })

                invoice_ids = self.env['sale.order'].search_read([('id', 'in', sale_orders.ids)], ['invoice_ids'])
                invoice_ids = list(itertools.chain(*[i['invoice_ids'] for i in invoice_ids]))
                invoice_ids = self.env['account.move'].search_read(
                    [('id', 'in', invoice_ids), ('move_type', '=', 'out_invoice')], ['id'])
                invoice_ids = list(map(lambda x: x['id'], invoice_ids))

                if invoice_ids:
                    stat_buttons.append({
                        'name': _('Invoices'),
                        'count': len(invoice_ids),
                        'icon': 'fa fa-pencil-square-o',
                        'action': _to_action_data(
                            action=self.env.ref('account.action_move_out_invoice_type'),
                            domain=[('id', 'in', invoice_ids), ('move_type', '=', 'out_invoice')],
                            context={'create': False, 'delete': False}
                        )
                    })

        ts_tree = self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        ts_form = self.env.ref('hr_timesheet.hr_timesheet_line_form')
        if self.env.company.timesheet_encode_uom_id == self.env.ref('uom.product_uom_day'):
            timesheet_label = [_('Days'), _('Recorded')]
        else:
            timesheet_label = [_('Hours'), _('Recorded')]

        stat_buttons.append({
            'name': timesheet_label,
            'count': sum(self.mapped('total_timesheet_time')),
            'icon': 'fa fa-calendar',
            'action': _to_action_data(
                'account.analytic.line',
                domain=[('project_id', 'in', self.ids)],
                views=[(ts_tree.id, 'list'), (ts_form.id, 'form')],
            )
        })

        return stat_buttons


class ProjectTask(models.Model):
    _inherit = 'project.task'

    plan_diff = fields.Integer('Plan Diff.',compute_sudo=True, store=True, compute='_get_plan_diff')
    forecast_hours = fields.Integer('Forecast Hours',store=True, compute_sudo=True, compute='_compute_forecast_hours', help="Number of hours forecast for this task (and its sub-tasks), rounded to the unit.")

    @staticmethod
    def _read_group_stage_ids(stages, domain, order):
        """
        Return all stages, ensuring they are displayed in the Kanban view,
        even if no tasks are associated with them.
        """
        return stages.search([], order=order)

    def _create(self, vals_list):
        vals = super(ProjectTask, self)._create(vals_list)

        # Loop through created records
        for task in vals:
            if not task.project_id:
                continue
            timesheets = task.timesheet_ids
            if timesheets:
                emp = timesheets.mapped('employee_id')
                forcecast = self.env['planning.slot'].search([('task_id', '=', task.id)]).exists()
                if emp:
                    for employee in emp:
                        if not forcecast.filtered(lambda s: s.employee_id.id == employee.id):
                            self.env['planning.slot'].sudo().create({
                                'employee_id': employee.id,
                                'task_id': task.id,
                                'project_id': task.project_id.id,
                                'allocated_hours': 0.00,
                            })
        return vals

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)

        # Loop through each task to handle multiple records
        for task in self:
            if not task.project_id:
                continue
            timesheets = task.timesheet_ids
            if timesheets:
                emp = timesheets.mapped('employee_id')
                forcecast = self.env['planning.slot'].search([('task_id', '=', task.id)]).exists()
                if emp:
                    for employee in emp:
                        if not forcecast.filtered(lambda s: s.employee_id.id == employee.id):
                            self.env['planning.slot'].sudo().create({
                                'employee_id': employee.id,
                                'task_id': task.id,
                                'project_id': task.project_id.id,
                                'allocated_hours': 0.00,
                            })
        return res

    @api.onchange('forecast_hours', 'planned_hours')
    def _get_plan_diff(self):
        for rec in self:
            rec.plan_diff = rec.planned_hours - rec.forecast_hours


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    name_tree = fields.Text('Description', compute='_get_name_tree', store=True)
    # plan_diff = fields.Integer('Plan Diff.', compute='_get_plan_diff')
    # allocated_hours = fields.Integer('Plan Hrs.', compute='_get_allocated_hours')
    planning_slot_id = fields.Many2one('planning.slot', 'Planning Slot')



    def _get_allocated_hours(self):
        for rec in self:
            time = self.env['planning.slot'].search([('id', '=', rec.planning_slot_id.id)])
            rec.allocated_hours = time.allocated_hours

    # def _get_plan_diff(self):
    #     for rec in self:
    #         rec.plan_diff = rec.unit_amount - rec.plan_time

    def _get_name_tree(self):
        for rec in self:
            max = 60
            if rec.name and not rec.name_tree:
                rec.name_tree = rec.name[:max]
            # else:
            #     rec.name_tree = None


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    plan_emp = fields.Integer('Plan emp', compute='_get_plan_emp')
    plan_diff = fields.Integer('Plan Diff.')
    hrs_spent = fields.Float('Hrs. Spent')


    # compute_sudo=True, store=True, readonly=False


    # @api.model
    # def create(self, vals_list):
    #     res = super(PlanningSlot, self).create(vals_list)
    #     for vals in vals_list:
    #         if isinstance(vals, dict):  # Check if vals is a dictionary
    #             self.env['account.analytic.line'].sudo().create({
    #                 'employee_id': vals.get('employee_id'),
    #                 'task_id': vals.get('task_id'),
    #                 'planning_slot_id': res.id,
    #                 'allocated_hours': res.id,
    #             })
    #     return res

    # @api.depends('task_id')
    # @api.depends(
    #     'start_datetime', 'end_datetime', 'employee_id.resource_calendar_id',
    #     'company_id.resource_calendar_id', 'allocated_percentage','task_id','employee_id')
    def _get_hrs_spent(self):
        for rec in self:
            if rec.employee_id.id==8 and rec.task_id.id==180:
                print("Here I AM")
            hrs = self.env['account.analytic.line'].search([
                ('task_id', '=', rec.task_id.id),
                ('employee_id', '=', rec.employee_id.id)
            ])
            total_hrs = sum(hr.unit_amount for hr in hrs)
            rec.hrs_spent = total_hrs


    @api.onchange('task_id')
    def _get_plan_emp(self):
        for rec in self:
            plan_emp = self.env['project.task'].search([('id', '=', rec.task_id.id)])
            rec.plan_emp = plan_emp.forecast_hours if plan_emp else 0
            rec._get_hrs_spent()
            rec._get_plan_diff()


    # @api.onchange('task_id')
    # @api.depends(
    #     'start_datetime', 'end_datetime', 'employee_id.resource_calendar_id',
    #     'company_id.resource_calendar_id', 'allocated_percentage')
    def _get_plan_diff(self):
        for rec in self:
            rec.plan_diff = rec.hrs_spent - rec.allocated_hours
            rec._get_hrs_spent()
