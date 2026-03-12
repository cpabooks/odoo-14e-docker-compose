from odoo import api, models, fields, _
from datetime import timedelta, datetime


class ActivityCreateWizard(models.TransientModel):
    _name = 'activity.create.wizard'
    _description = 'Activity Create Wizard'

    number = fields.Integer('Number of Activities', default=12)
    task_id = fields.Many2one('project.task', 'Task', required=True)
    activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', required=True)

    def action_create(self):
        res_model_id = self.env['ir.model'].search([('model', '=', 'project.task')], limit=1)
        for rec in self:
            if rec.task_id and rec.task_id.recurring_task:
                repeat = None
                if rec.task_id.repeat_unit == 'day':
                    repeat = 1
                elif rec.task_id.repeat_unit == 'week':
                    repeat = 7
                elif rec.task_id.repeat_unit == 'month':
                    repeat = 30
                elif rec.task_id.repeat_unit == 'year':
                    repeat = 365

                days = []
                if rec.task_id.mon:
                    days.append('mon')
                if rec.task_id.tue:
                    days.append('tue')
                if rec.task_id.wed:
                    days.append('wed')
                if rec.task_id.thu:
                    days.append('thu')
                if rec.task_id.fri:
                    days.append('fri')
                if rec.task_id.sat:
                    days.append('sat')
                if rec.task_id.sun:
                    days.append('sun')

                current_date = datetime.now().date()
                task_created = 0
                while task_created < rec.number:
                    if repeat == 1:  # Daily recurrence
                        next_date = current_date + timedelta(days=1)
                    elif repeat == 7:  # Weekly recurrence
                        next_date = current_date + timedelta(days=7)
                    elif repeat in [30, 365]:  # Monthly or Yearly recurrence
                        next_date = current_date + timedelta(days=repeat)

                        # Adjust to nearest same weekday if required
                        if days:
                            day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
                            while next_date.strftime('%a').lower()[:3] not in days:
                                next_date += timedelta(days=1)


                    # Create activity on 'mail.activity'
                    self.env['mail.activity'].create({
                        'res_model': 'project.task',
                        'res_id': rec.task_id.id,
                        'activity_type_id': rec.task_id.activity_type_id.id,  # Assuming activity_type_id is set
                        'summary': f'Activity {task_created + 1}',
                        'date_deadline': next_date,
                        'user_id': rec.task_id.user_id.id,  # Assuming assigned user is defined
                        'res_model_id': res_model_id.id if res_model_id else False,  # Assuming assigned user is defined
                    })

                    current_date = next_date
                    task_created += 1

                print(f"Activities Created: {task_created}")
                print(f"Days: {days}")
                print(f"Repeat Interval: {repeat}")
