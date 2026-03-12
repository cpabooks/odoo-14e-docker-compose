# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, api, models
from dateutil.relativedelta import relativedelta
import datetime


class ResUsers(models.Model):

    _inherit = 'res.users'

    # Store user login history records
    login_history_ids = fields.One2many(
        'user.login.history', 'user_id', string='User Login History')

    # Method call when user login, create history record here
    @api.model
    def _update_last_login(self):
        log = self.env['res.users.log'].create({})
        self.env['user.login.history'].create(
            {'user_id': self.id, 'login_time': log.create_date})

    # Login History smart button action
    def action_view_login_history(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "User Login History",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'user.login.history',
            'domain': [('user_id', '=', self.id)]
        }

    def run_remove_user_login_history(self):

        login_history = self.env['user.login.history'].search([])

        for history in login_history:
            previous_month = datetime.datetime.now() - relativedelta(months=1)

            if history.login_time <= previous_month:
                history.unlink()
