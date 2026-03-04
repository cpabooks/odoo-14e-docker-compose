from odoo import api, models, fields, _


class JournalMessageWizard(models.TransientModel):
    _name = 'journal.message.wizard'
    _description = 'Journal Message Wizard'

    message = fields.Text('Message')