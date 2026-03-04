from odoo import models, api, _
from odoo.tools.misc import format_date


class ReportAccountAgedReceivable(models.Model):
    _inherit = "account.aged.receivable"

    @api.model
    def _get_report_name(self):
        return _("Aged Receivable Report")


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    @api.model
    def _get_column_details(self, options):
        return [
            self._header_column(),
            # self._field_column('report_date'),
            # self._field_column('journal_code', name="Journal"),
            # self._field_column('account_name', name="Account"),
            # self._field_column('expected_pay_date'),
            self._field_column('period0', name=_("As of: %s") % format_date(self.env, options['date']['date_to'])),
            self._field_column('period1', sortable=True),
            self._field_column('period2', sortable=True),
            self._field_column('period3', sortable=True),
            self._field_column('period4', sortable=True),
            self._field_column('period5', sortable=True),
            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_('Total'),
                classes=['number'],
                formatter=self.format_value,
                getter=(
                    lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v['period5']),
                sortable=True,
            ),
        ]

    def _get_hierarchy_details(self, options):
        return [
            self._hierarchy_level('partner_id', foldable=True, namespan=1),
            self._hierarchy_level('id'),
        ]

    def _format_total_line(self, res, value_dict, options):
        res['name'] = _('Total')
        res['colspan'] = 1
        res['columns'] = res['columns'][0:]
