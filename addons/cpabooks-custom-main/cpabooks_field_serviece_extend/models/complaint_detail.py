from odoo import api, models, fields, _

class ComplaintList(models.Model):
    _name = 'complaint.detail'
    _description = 'Contact Person'

    name = fields.Char(required=True)