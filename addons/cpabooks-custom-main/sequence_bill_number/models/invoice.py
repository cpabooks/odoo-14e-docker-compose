
from odoo import api, fields, models

#Display amount in words in Sale order
class AccountMove(models.Model):

    _inherit = 'account.move'

    sequence_bill_number = fields.Integer(sting="Order Number")

