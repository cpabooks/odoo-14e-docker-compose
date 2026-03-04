import itertools

# from addons.web.controllers.main import clean_action
from odoo.addons.web.controllers.main import clean_action
from odoo import models, fields, api, _
import json
from odoo.tools import float_round
from odoo.osv import expression

class ProjectInherit(models.Model):
    _inherit = 'project.project'

    def _compute_project_issue_count(self):
        count = self.env["stock.picking"].sudo().search_count([('issue_project_id', 'in', self.ids)])
        for project in self:
            project.project_issue_count = count

    def _compute_task_count(self):
        task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', '&', ('stage_id.is_closed', '=', False), ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)


    project_issue_count = fields.Integer(string="Stock Issued", compute='_compute_project_issue_count')



    def project_tree_view(self):
        return {
            'name': _('Issue Note'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('cpabooks_project_issue_note.issue_tree').id, 'tree'),
                      (self.env.ref('cpabooks_project_issue_note.issue_form').id, 'form'), (False, 'kanban')],
            'domain': [('issue_project_id', 'in', self.ids)],
            # 'context': {'search_default_group_by_payment_method': 1}
        }


    def _plan_get_stat_button(self):
        stat_buttons=super(ProjectInherit, self)._plan_get_stat_button()
        count = self.env["stock.picking"].sudo().search_count([('issue_project_id', '=', self.ids)])
        # if count == 1:
        issue_domain=[('issue_project_id', 'in', self.ids)]
        issue_context=self.env.context.copy()
        issue_context.pop('search_default_name', False)
        # action_data = _to_action_data('stock.picking',
        #                                   views=[[self.env.ref('cpabooks_project_issue_note.issue_tree').id, 'tree'],[self.env.ref('cpabooks_project_issue_note.issue_form').id, 'form'], [False, 'kanban']],
        #                               domain=[('project_id', '=', self.ids)])
        #
        # stat_buttons.append({
        #     'name': _('Stock Issue'),
        #     'count': count,
        #     'icon': 'fa fa-puzzle-piece',
        #     'action': action_data
        # })
        stat_buttons.append({
            'name': _('Stock Issued'),
            'count': count,
            'icon': 'fa fa-puzzle-piece',
            'action': _to_action_data(
                action=self.env.ref('cpabooks_project_issue_note.issue_action'),
                domain=issue_domain,
                context=issue_context
            )
        })
        return stat_buttons

    def _plan_prepare_values(self):
        currency = self.env.company.currency_id
        uom_hour = self.env.ref('uom.product_uom_hour')
        company_uom = self.env.company.timesheet_encode_uom_id
        is_uom_day = company_uom == self.env.ref('uom.product_uom_day')
        hour_rounding = uom_hour.rounding
        billable_types = ['non_billable', 'non_billable_project', 'billable_time', 'non_billable_timesheet', 'billable_fixed']

        values = {
            'projects': self,
            'currency': currency,
            'timesheet_domain': [('project_id', 'in', self.ids)],
            'profitability_domain': [('project_id', 'in', self.ids)],
            'stat_buttons': self._plan_get_stat_button(),
            'is_uom_day': is_uom_day,
        }

        #
        # Hours, Rates and Profitability
        #
        dashboard_values = {
            'time': dict.fromkeys(billable_types + ['total'], 0.0),
            'rates': dict.fromkeys(billable_types + ['total'], 0.0),
            'profit': {
                'invoiced': 0.0,
                'to_invoice': 0.0,
                'cost': 0.0,
                'issue_cost':0.0,
                'total': 0.0,
            }
        }

        # hours from non-invoiced timesheets that are linked to canceled so
        canceled_hours_domain = [('project_id', 'in', self.ids), ('timesheet_invoice_type', '!=', False), ('so_line.state', '=', 'cancel')]
        total_canceled_hours = sum(self.env['account.analytic.line'].search(canceled_hours_domain).mapped('unit_amount'))
        canceled_hours = float_round(total_canceled_hours, precision_rounding=hour_rounding)
        if is_uom_day:
            # convert time from hours to days
            canceled_hours = round(uom_hour._compute_quantity(canceled_hours, company_uom, raise_if_failure=False), 2)
        dashboard_values['time']['canceled'] = canceled_hours
        dashboard_values['time']['total'] += canceled_hours

        # hours (from timesheet) and rates (by billable type)
        dashboard_domain = [('project_id', 'in', self.ids), ('timesheet_invoice_type', '!=', False), '|', ('so_line', '=', False), ('so_line.state', '!=', 'cancel')]  # force billable type
        dashboard_data = self.env['account.analytic.line'].read_group(dashboard_domain, ['unit_amount', 'timesheet_invoice_type'], ['timesheet_invoice_type'])
        dashboard_total_hours = sum([data['unit_amount'] for data in dashboard_data]) + total_canceled_hours
        for data in dashboard_data:
            billable_type = data['timesheet_invoice_type']
            amount = float_round(data.get('unit_amount'), precision_rounding=hour_rounding)
            if is_uom_day:
                # convert time from hours to days
                amount = round(uom_hour._compute_quantity(amount, company_uom, raise_if_failure=False), 2)
            dashboard_values['time'][billable_type] = amount
            dashboard_values['time']['total'] += amount
            # rates
            rate = round(data.get('unit_amount') / dashboard_total_hours * 100, 2) if dashboard_total_hours else 0.0
            dashboard_values['rates'][billable_type] = rate
            dashboard_values['rates']['total'] += rate
        dashboard_values['time']['total'] = round(dashboard_values['time']['total'], 2)

        # rates from non-invoiced timesheets that are linked to canceled so
        dashboard_values['rates']['canceled'] = float_round(100 * total_canceled_hours / (dashboard_total_hours or 1), precision_rounding=hour_rounding)

        other_revenues = self.env['account.analytic.line'].read_group([
            ('account_id', 'in', self.analytic_account_id.ids),
            ('amount', '>=', 0),
            ('project_id', '=', False)], ['amount'], [])[0].get('amount', 0)
        get_picking=self.env['stock.picking'].sudo().search([('issue_project_id','in',self.ids)])
        issue_cost=sum(get_picking.move_ids_without_package.mapped('amount'))

        # profitability, using profitability SQL report
        profit = dict.fromkeys(['invoiced', 'to_invoice', 'cost','issue_cost', 'expense_cost', 'expense_amount_untaxed_invoiced', 'total'], 0.0)
        profitability_raw_data = self.env['project.profitability.report'].read_group([('project_id', 'in', self.ids)], ['project_id', 'amount_untaxed_to_invoice', 'amount_untaxed_invoiced', 'timesheet_cost', 'expense_cost', 'expense_amount_untaxed_invoiced'], ['project_id'])
        for data in profitability_raw_data:
            profit['invoiced'] += data.get('amount_untaxed_invoiced', 0.0)
            profit['to_invoice'] += data.get('amount_untaxed_to_invoice', 0.0)
            profit['cost'] += data.get('timesheet_cost', 0.0)
            profit['expense_cost'] += data.get('expense_cost', 0.0)
            profit['expense_amount_untaxed_invoiced'] += data.get('expense_amount_untaxed_invoiced', 0.0)
        profit['other_revenues'] = other_revenues or 0
        profit['issue_cost']= (-1)*issue_cost or 0
        profit['total'] = sum([profit[item] for item in profit.keys()])
        dashboard_values['profit'] = profit

        values['dashboard'] = dashboard_values

        #
        # Time Repartition (per employee per billable types)
        #
        user_ids = self.env['project.task'].sudo().read_group([('project_id', 'in', self.ids), ('user_id', '!=', False)], ['user_id'], ['user_id'])
        user_ids = [user_id['user_id'][0] for user_id in user_ids]
        employee_ids = self.env['res.users'].sudo().search_read([('id', 'in', user_ids)], ['employee_ids'])
        # flatten the list of list
        employee_ids = list(itertools.chain.from_iterable([employee_id['employee_ids'] for employee_id in employee_ids]))

        aal_employee_ids = self.env['account.analytic.line'].read_group([('project_id', 'in', self.ids), ('employee_id', '!=', False)], ['employee_id'], ['employee_id'])
        employee_ids.extend(list(map(lambda x: x['employee_id'][0], aal_employee_ids)))

        # Retrieve the employees for which the current user can see theirs timesheets
        employee_domain = expression.AND([[('company_id', 'in', self.env.companies.ids)], self.env['account.analytic.line']._domain_employee_id()])
        employees = self.env['hr.employee'].sudo().browse(employee_ids).filtered_domain(employee_domain)
        repartition_domain = [('project_id', 'in', self.ids), ('employee_id', '!=', False), ('timesheet_invoice_type', '!=', False)]  # force billable type
        # repartition data, without timesheet on cancelled so
        repartition_data = self.env['account.analytic.line'].read_group(repartition_domain + ['|', ('so_line', '=', False), ('so_line.state', '!=', 'cancel')], ['employee_id', 'timesheet_invoice_type', 'unit_amount'], ['employee_id', 'timesheet_invoice_type'], lazy=False)
        # read timesheet on cancelled so
        cancelled_so_timesheet = self.env['account.analytic.line'].read_group(repartition_domain + [('so_line.state', '=', 'cancel')], ['employee_id', 'unit_amount'], ['employee_id'], lazy=False)
        repartition_data += [{**canceled, 'timesheet_invoice_type': 'canceled'} for canceled in cancelled_so_timesheet]

        # set repartition per type per employee
        repartition_employee = {}
        for employee in employees:
            repartition_employee[employee.id] = dict(
                employee_id=employee.id,
                employee_name=employee.name,
                non_billable_project=0.0,
                non_billable=0.0,
                billable_time=0.0,
                non_billable_timesheet=0.0,
                billable_fixed=0.0,
                canceled=0.0,
                total=0.0,
            )
        for data in repartition_data:
            employee_id = data['employee_id'][0]
            repartition_employee.setdefault(employee_id, dict(
                employee_id=data['employee_id'][0],
                employee_name=data['employee_id'][1],
                non_billable_project=0.0,
                non_billable=0.0,
                billable_time=0.0,
                non_billable_timesheet=0.0,
                billable_fixed=0.0,
                canceled=0.0,
                total=0.0,
            ))[data['timesheet_invoice_type']] = float_round(data.get('unit_amount', 0.0), precision_rounding=hour_rounding)
            repartition_employee[employee_id]['__domain_' + data['timesheet_invoice_type']] = data['__domain']
        # compute total
        for employee_id, vals in repartition_employee.items():
            repartition_employee[employee_id]['total'] = sum([vals[inv_type] for inv_type in [*billable_types, 'canceled']])
            if is_uom_day:
                # convert all times from hours to days
                for time_type in ['non_billable_project', 'non_billable', 'billable_time', 'non_billable_timesheet', 'billable_fixed', 'canceled', 'total']:
                    if repartition_employee[employee_id][time_type]:
                        repartition_employee[employee_id][time_type] = round(uom_hour._compute_quantity(repartition_employee[employee_id][time_type], company_uom, raise_if_failure=False), 2)
        hours_per_employee = [repartition_employee[employee_id]['total'] for employee_id in repartition_employee]
        values['repartition_employee_max'] = (max(hours_per_employee) if hours_per_employee else 1) or 1
        values['repartition_employee'] = repartition_employee

        #
        # Table grouped by SO / SOL / Employees
        #
        timesheet_forecast_table_rows = self._table_get_line_values(employees)
        if timesheet_forecast_table_rows:
            values['timesheet_forecast_table'] = timesheet_forecast_table_rows
        return values

def _to_action_data(model=None, *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = clean_action(action.read()[0], env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None: # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr