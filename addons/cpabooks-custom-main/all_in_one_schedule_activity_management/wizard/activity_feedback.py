from odoo import api, models, fields, _

class ActivityFeedback(models.TransientModel):
    _name = 'activity.feedback'
    _description = 'Activity Feedback'

    message = fields.Text('Feedback')
    activity_id = fields.Many2one('mail.activity', 'Activity')

    def action_done(self):
        for rec in self:
            if rec.activity_id:
                rec.activity_id.action_set_activity_done(rec.message)
