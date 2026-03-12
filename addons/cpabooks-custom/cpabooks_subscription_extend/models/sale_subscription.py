from soupsieve.css_types import pickle_register

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def _set_inv_date(self, inv, inv_date):
        """Update invoice_date and invoice_date_due"""
        if inv:
            for invoice in inv:
                if invoice:
                    invoice.write({
                        'invoice_date': inv_date if inv_date else self.date_start,
                        'invoice_date_due': inv_date if inv_date else self.date_start
                    })
                self._cr.commit()

    def create_multiple_invoices(self):
        """Generate multiple invoices until recurring_next_date matches rec.date."""
        cr = self.env.cr
        for rec in self:
            if rec.recurring_next_date and rec.date:
                trial = 0
                while rec.recurring_next_date <= rec.date:
                    inv_date = rec.recurring_next_date
                    # Stop when the next date matches the expected date
                    if rec.recurring_next_date == rec.date:
                        break

                    inv = rec._recurring_create_invoice()
                    rec._set_inv_date(inv, inv_date)
                    trial += 1
                    cr.commit()