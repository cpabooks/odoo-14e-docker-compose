import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class TechnicalSpec(models.Model):
    _name = 'technical.spec'
    
    order_id=fields.Many2one('sale.order')
    name=fields.Char()
    label_name=fields.Many2one('technical.spec.label',string="Label")
    description=fields.Many2one('technical.spec.description', string="description")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)

class TechnicalSpeclabel(models.Model):
    _name = 'technical.spec.label'

    name=fields.Char(string="label")


class TechnicalSpecDescription(models.Model):
    _name = 'technical.spec.description'

    name = fields.Char(string="Description")