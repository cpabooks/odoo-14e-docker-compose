from odoo import api, models, fields, _

class DailySalesReportWizard(models.TransientModel):
    _name = 'daily.sales.report.wizard'
    _description = 'Daily Sales Report Wizard'

    