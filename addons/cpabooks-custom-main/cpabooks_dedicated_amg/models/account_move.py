from odoo import fields, models,api


class accountMove(models.Model):
    _inherit = 'account.move'

    vehicle_name=fields.Char(string="Vehicle Name")
    vehicle_no=fields.Char(string="Vehicle Number")
    kilometer=fields.Char(string="Kilometer")
    claim_no=fields.Char(string="Claim Number")