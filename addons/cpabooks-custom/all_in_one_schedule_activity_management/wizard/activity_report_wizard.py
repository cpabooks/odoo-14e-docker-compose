from odoo import api, models, fields, _
from datetime import timedelta

class ActivityReportWizard(models.TransientModel):
    _name = "activity.report.wizard"
    _description = "Activity Report Wizard"

    user_id = fields.Many2one(
        'res.users',
        string='Activity For',
        default=lambda self: self.env.user.id
    )
    date_report = fields.Date(
        string='Date',
        default=fields.Date.today()
    )

    def action_print_pdf(self):
        previous_date = self.date_report - timedelta(days=1)
        next_date = self.date_report + timedelta(days=1)
        Activity = self.env['mail.activity']

        # Previous activities
        prev_acts = Activity.search([
            ('date_deadline', '<=', previous_date),
            ('user_id', '=', self.user_id.id),
            ('state', 'not in', ['done', 'cancel'])
        ])
        prev_acts = prev_acts.filtered(
            lambda a: (a.date_deadline == previous_date) or (a.state != 'done')
        )

        # Report date activities
        rep_acts = Activity.search([
            ('date_deadline', '=', self.date_report),
            ('user_id', '=', self.user_id.id),
            ('state', 'not in', ['done', 'cancel'])
        ])

        filtered_acts = rep_acts.filtered(
            lambda a: a.create_date.date() != self.date_report
        )
        act_unplanned = rep_acts.filtered(
            lambda a: a.create_date.date() == self.date_report
        )

        # Next activities
        next_acts = Activity.search([
            ('date_deadline', '=', next_date),
            ('user_id', '=', self.user_id.id),
            ('state', 'not in', ['done', 'cancel'])
        ])

        def get_state_value(act):
            return dict(Activity._fields['state'].selection).get(act.state, act.state)

        prev_data, rep_data, next_data = [], [], []

        # Previous
        for act in prev_acts:
            act_dict = {'name': act.summary or act.display_name, 'state': get_state_value(act)}
            prev_data.append(act_dict)
            if act.state != 'done':
                rep_data.append(act_dict)

        # Report date
        for act in filtered_acts:
            rep_data.append({'name': act.summary or act.display_name, 'state': get_state_value(act)})

        # Next
        next_data = [{'name': act.summary or act.display_name, 'state': get_state_value(act)} for act in next_acts]

        # Unplanned
        act_unplanned = [{'name': a.summary or a.display_name, 'state': get_state_value(a)} for a in act_unplanned]

        # Merge rows
        all_names = set([a['name'] for a in prev_data] + [a['name'] for a in rep_data] + [a['name'] for a in next_data])
        rows = []
        for name in sorted(all_names):
            rows.append({
                'name': name,
                'previous_state': next((a['state'] for a in prev_data if a['name'] == name), None),
                'report_state': next((a['state'] for a in rep_data if a['name'] == name), None),
                'next_state': next((a['state'] for a in next_data if a['name'] == name), None),
            })

        data = {
            'form': self.read()[0],
            'rows': rows,
            'act_unplanned': act_unplanned,
            'user_name': self.user_id.name,
            'date_prev': previous_date,
            'date_report': self.date_report,
            'date_next': next_date,
        }

        return self.env.ref(
            "all_in_one_schedule_activity_management.action_report_activity_report"
        ).report_action(self, data=data)
