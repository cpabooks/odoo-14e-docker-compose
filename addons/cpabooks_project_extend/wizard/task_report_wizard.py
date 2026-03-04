from odoo import api, models, fields
from datetime import timedelta, datetime, time
from odoo.exceptions import ValidationError

class TaskReport(models.TransientModel):
    _name = 'task.report.wizard'
    _description = 'Task Report'

    user_id = fields.Many2one('res.users', 'Tasks For', required=True, default=lambda self: self.env.user)
    date = fields.Date('Date', required=True, default=fields.Date.context_today)

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(TaskReport, self).default_get(fields_list)
    #     print(res)
    #     return res

    # def action_print_report(self):
    #     previous_date = self.date - timedelta(days=1)
    #     next_date = self.date + timedelta(days=1)
    #
    #     Task = self.env['project.task']
    #
    #     tasks_in_range = Task.search([
    #         ('user_id', '=', self.user_id.id),
    #         ('date_start', '>=', previous_date),
    #         ('date_start', '<=', self.date)
    #     ])
    #
    #     prev_ids = []
    #     report_day_ids = []
    #
    #     for task in tasks_in_range:
    #         if task.date_start == previous_date:
    #             prev_ids.append(task.id)
    #             if task.state != 'done':
    #                 report_day_ids.append(task.id)
    #         else:
    #             report_day_ids.append(task.id)
    #
    #     next_tasks = Task.search([
    #         ('user_id', '=', self.user_id.id),
    #         ('date_start', '=', next_date)
    #     ])
    #
    #     def get_state_value(task):
    #         return dict(Task._fields['state'].selection).get(task.state)
    #
    #     tasks = {
    #         'previous_date': [{'name': t.name, 'state': get_state_value(t)} for t in Task.browse(prev_ids) if t],
    #         'report_date': [{'name': t.name, 'state': get_state_value(t)} for t in Task.browse(report_day_ids) if t],
    #         'next_date': [{'name': t.name, 'state': get_state_value(t)} for t in next_tasks if t]
    #     }
    #
    #     rows = max(len(tasks['previous_date']), len(tasks['report_date']), len(tasks['next_date']))
    #
    #     data = {
    #         'form': self.read()[0],
    #         'tasks': tasks,
    #         'user': self.user_id,
    #         'rows': rows,
    #         'date_prev': previous_date,
    #         'date_report': self.date,
    #         'date_next': next_date,
    #     }
    #
    #     return self.env.ref('cpabooks_project_extend.action_task_report').report_action(self, data=data)

    def action_print_report(self):
        previous_date = self.date - timedelta(days=1)
        next_date = self.date + timedelta(days=1)

        Task = self.env['project.task']

        # Get tasks for each date range
        prev_task_ids = [t.id for t in Task.search([
            ('user_id', '=', self.user_id.id),
            ('date_start', '<=', previous_date),
            ('state', 'in', ['done', 'in_progress'])
        ]) if (t.state != 'done' and t.date_start != previous_date) or (t.date_start == previous_date)]


        previous_tasks = Task.browse(prev_task_ids)

        report_tasks = Task.search([
            '|', ('date_end', '=', self.date), ('date_start', '=', self.date),
            ('user_id', '=', self.user_id.id),
            ('state', 'in', ['done', 'in_progress'])
        ])

        filtered_tasks = report_tasks.filtered(
            lambda t: t.create_date.date() != self.date
        )

        task_unplaned = report_tasks.filtered(
            lambda t: t.create_date.date() == self.date
        )

        next_tasks = Task.search([
            ('user_id', '=', self.user_id.id),
            ('date_start', '=', next_date),
            ('state', 'in', ['done', 'in_progress'])
        ])



        def get_state_value(task):
            return dict(Task._fields['state'].selection).get(task.state)

        # Prepare task data with original logic
        previous_data = []
        report_data = []

        # Previous date tasks - add to previous_data and to report_data if not done
        for task in previous_tasks:
            task_dict = {
                'name': task.name,
                'state': get_state_value(task)
            }
            previous_data.append(task_dict)
            if task.state != 'done':
                report_data.append(task_dict)  # Add to report date if not done

        # Report date tasks - add to report_data
        for task in filtered_tasks:
            report_data.append({
                'name': task.name,
                'state': get_state_value(task)
            })

        # Next date tasks
        next_data = [{
            'name': task.name,
            'state': get_state_value(task)
        } for task in next_tasks]

        task_unplaned = [{
            'name': t.name,
            'state': get_state_value(t)
        } for t in task_unplaned]

        # Create unified rows matching tasks by name
        all_task_names = set()
        all_task_names.update(t['name'] for t in previous_data)
        all_task_names.update(t['name'] for t in report_data)
        all_task_names.update(t['name'] for t in next_data)

        rows = []
        for task_name in sorted(all_task_names):
            row = {
                'name': task_name,
                'previous_state': None,
                'report_state': None,
                'next_state': None
            }

            # Find in previous data
            for task in previous_data:
                if task['name'] == task_name:
                    row['previous_state'] = task['state']
                    break

            # Find in report data
            for task in report_data:
                if task['name'] == task_name:
                    row['report_state'] = task['state']
                    break

            # Find in next data
            for task in next_data:
                if task['name'] == task_name:
                    row['next_state'] = task['state']
                    break

            rows.append(row)

        print(self.user_id.name)

        data = {
            'form': self.read()[0],
            'rows': rows,
            'task_unplaned': task_unplaned,
            'user_name': self.user_id.name,
            'date_prev': previous_date,
            'date_report': self.date,
            'date_next': next_date,
        }

        return self.env.ref('cpabooks_project_extend.action_task_report').report_action(self, data=data)