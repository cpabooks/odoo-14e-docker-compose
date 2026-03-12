from odoo import api, models, fields, _

class CpabooksDisclaimer(models.Model):
    _name = 'cpabooks.disclaimer'
    _description = 'CPAbooks Disclaimer'

    disclaimer = fields.Text('Disclaimer Deliver Note')
