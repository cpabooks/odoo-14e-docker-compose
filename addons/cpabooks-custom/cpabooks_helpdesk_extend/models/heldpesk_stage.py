from odoo import api, models, fields

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.stage'

    @api.model
    def _default_team_ids(self):
        team_records = self.env['helpdesk.team'].search([])
        return [(6, 0, team_records.ids)]

    team_ids = fields.Many2many(
        'helpdesk.team', relation='team_stage_rel', string='Team',
        default=_default_team_ids,
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.'
    )

    ticket_state = fields.Selection([
        ('draft', 'Pending Review'),
        # ('new', 'New'),
        # ('approve', 'Approve'),
        # ('reviewed', 'Reviewed'),
        ('submit_for_approval', 'Pending Approval'),
        ('dev', 'Development In-Progress'),
        ('test', 'Pending Dev_test'),
        ('updating', 'Pending Client_update'),
        ('done', 'Updated to clients'),
        ('cancel', 'Cancelled')
    ],
        string="Ticket Status",
        tracking=True)

    _sql_constraints = [
        ('unique_ticket_stage', 'unique (ticket_state)', 'The Ticket state should not repiet..'),
    ]

    def action_select_all(self):
        all_teams = self.env['helpdesk.team'].search([])
        self.team_ids = [(6, 0, all_teams.ids)]

        return None







class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    @api.model
    def create(self, vals):
        new_team = super(HelpdeskTeam, self).create(vals)
        stages = self.env['helpdesk.stage'].search([])
        for stage in stages:
            stage.team_ids |= new_team
        return new_team
