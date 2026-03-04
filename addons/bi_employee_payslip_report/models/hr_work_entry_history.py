from lxml import etree

from odoo import _, api, exceptions, fields, models


class WorkEntryHistory(models.Model):
    _inherit = "hr.work.entry.history"

    emp_id=fields.Many2one('hr.employee')
    pre_date_start=fields.Datetime()
    pre_date_stop=fields.Datetime()