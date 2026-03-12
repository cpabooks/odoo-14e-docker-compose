# _*_ coding: utf-8
from odoo import models, fields, api, _
from datetime import datetime

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}

class InsFinancialReportXlsx(models.AbstractModel):
    _name = 'report.dynamic_xlsx.ins_financial_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def _define_formats(self, workbook):
        """ Add cell formats to current workbook. Available formats: * format_title * format_header """
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'border': False,
            'font': 'Arial',
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': False
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'bottom': False
        })
        line_header_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'bottom': True
        })
        line_header_string = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'bottom': False
        })
        line_header_string_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'bottom': True
        })
        return {
            'format_title': format_title,
            'format_header': format_header,
            'content_header': content_header,
            'content_header_date': content_header_date,
            'line_header': line_header,
            'line_header_bold': line_header_bold,
            'line_header_string': line_header_string,
            'line_header_string_bold': line_header_string_bold,
        }

    def prepare_report_filters(self, filter, sheet_2, formats):
        """It is writing under second page"""
        row_pos_2 = 2
        if filter:
            # Date from
            sheet_2.write_string(row_pos_2, 0, _('Date from'), formats['format_header'])
            date = self.convert_to_date(filter['form']['date_from'] and filter['form']['date_from'].strftime('%Y-%m-%d'))
            if filter['form'].get('date_from'):
                sheet_2.write_datetime(row_pos_2, 1, date, formats['content_header_date'])
            row_pos_2 += 1
            # Date to
            sheet_2.write_string(row_pos_2, 0, _('Date to'), formats['format_header'])
            date = self.convert_to_date(filter['form']['date_to'] and filter['form']['date_to'].strftime('%Y-%m-%d'))
            if filter['form'].get('date_to'):
                sheet_2.write_datetime(row_pos_2, 1, date, formats['content_header_date'])
            row_pos_2 += 1
            if filter['form']['enable_filter']:
                # Comparison Date from
                sheet_2.write_string(row_pos_2, 0, _('Comparison Date from'), formats['format_header'])
                date = self.convert_to_date(filter['form']['comparison_context']['date_from'] and filter['form']['comparison_context']['date_from'].strftime('%Y-%m-%d'))
                if filter['form']['comparison_context'].get('date_from'):
                    sheet_2.write_datetime(row_pos_2, 1, date, formats['content_header_date'])
                row_pos_2 += 1
                # Comparison Date to
                sheet_2.write_string(row_pos_2, 0, _('Comparison Date to'), formats['format_header'])
                date = self.convert_to_date(filter['form']['comparison_context']['date_to'] and filter['form']['comparison_context']['date_to'].strftime('%Y-%m-%d'))
                if filter['form']['comparison_context'].get('date_to'):
                    sheet_2.write_datetime(row_pos_2, 1, date, formats['content_header_date'])

    def prepare_report_contents(self, data, sheet, formats):
        row_pos = 3

        if data['form'].get('month_list'):
            sheet.set_column(0, 0, 50)
            sheet.set_column(1, 1, 15)
            sheet.set_column(2, 2, 15)
            sheet.set_column(3, 3, 15)
            sheet.set_column(4, 4, 15)
            sheet.set_column(5, 5, 15)
            sheet.set_column(6, 6, 15)
            sheet.set_column(7, 7, 15)
            sheet.set_column(8, 8, 15)
            sheet.set_column(9, 9, 15)
            sheet.set_column(10, 10, 15)
            sheet.set_column(11, 11, 15)

            # Heading
            sheet.write_string(row_pos, 0, _('Name'), formats['format_header'])
            j = 1
            for month_n in data['form']['month_list']:
                sheet.write_string(row_pos, j, _(month_n), formats['format_header'])
                j += 1

            # lines
            for a in data['report_lines']:
                if a['level'] == 2:
                    row_pos += 1
                row_pos += 1
                if a.get('account', False):
                    tmp_style_str = formats['line_header_string']
                    tmp_style_num = formats['line_header']
                else:
                    tmp_style_str = formats['line_header_string_bold']
                    tmp_style_num = formats['line_header_bold']
                sheet.write_string(row_pos, 0, '   ' * len(a.get('list_len', [])) + a.get('name'), tmp_style_str)
                j = 1
                for month_n in data['form']['month_list']:
                    sheet.write_number(row_pos, j, float(a.get(month_n)), tmp_style_num)
                    j += 1
        else:

            if data['form']['debit_credit'] == 1:
                sheet.set_column(0, 0, 90)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 15)
                sheet.set_column(3, 3, 15)

                sheet.write_string(row_pos, 0, _('Name'), formats['format_header'])
                sheet.write_string(row_pos, 1, _('Debit'), formats['format_header'])
                sheet.write_string(row_pos, 2, _('Credit'), formats['format_header'])
                sheet.write_string(row_pos, 3, _('Balance'), formats['format_header'])

                for a in data['report_lines']:
                    if a['level'] == 2:
                        row_pos += 1
                    row_pos += 1
                    if a.get('account', False):
                        tmp_style_str = formats['line_header_string']
                        tmp_style_num = formats['line_header']
                    else:
                        tmp_style_str = formats['line_header_string_bold']
                        tmp_style_num = formats['line_header_bold']
                    sheet.write_string(row_pos, 0, '   ' * len(a.get('list_len', [])) + a.get('name'), tmp_style_str)
                    sheet.write_number(row_pos, 1, float(a.get('debit')), tmp_style_num)
                    sheet.write_number(row_pos, 2, float(a.get('credit')), tmp_style_num)
                    sheet.write_number(row_pos, 3, float(a.get('balance')), tmp_style_num)
            else:
                sheet.set_column(0, 0, 90)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 15)

                sheet.write_string(row_pos, 0, _('Name'), formats['format_header'])
                if data['form']['enable_filter']:
                    sheet.write_string(row_pos, 1, data['form']['label_filter'], formats['format_header'])
                    sheet.write_string(row_pos, 2, _('Balance'), formats['format_header'])
                else:
                    sheet.write_string(row_pos, 1, _('Balance'), formats['format_header'])

                for a in data['report_lines']:
                    if a['level'] == 2:
                        row_pos += 1
                    row_pos += 1
                    if a.get('account', False):
                        tmp_style_str = formats['line_header_string']
                        tmp_style_num = formats['line_header']
                    else:
                        tmp_style_str = formats['line_header_string_bold']
                        tmp_style_num = formats['line_header_bold']
                    sheet.write_string(row_pos, 0, '   ' * len(a.get('list_len', [])) + a.get('name'), tmp_style_str)
                    if data['form']['enable_filter']:
                        sheet.write_number(row_pos, 1, float(a.get('balance_cmp')), tmp_style_num)
                        sheet.write_number(row_pos, 2, float(a.get('balance')), tmp_style_num)
                    else:
                        sheet.write_number(row_pos, 1, float(a.get('balance')), tmp_style_num)

        if data.get('initial_balance') or data.get('current_balance') or data.get('ending_balance'):
            row_pos += 2

            if data['form']['debit_credit'] == 1:
                sheet.merge_range(row_pos, 1, row_pos, 2, 'Initial Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 3, float(data.get('initial_balance')), tmp_style_num)
                row_pos += 1
                sheet.merge_range(row_pos, 1, row_pos, 2, 'Current Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 3, float(data.get('current_balance')), tmp_style_num)
                row_pos += 1
                sheet.merge_range(row_pos, 1, row_pos, 2, 'Net Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 3, float(data.get('ending_balance')), tmp_style_num)
            else:
                sheet.write_string(row_pos, 0, 'Initial Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 1, float(data.get('initial_balance')), tmp_style_num)
                row_pos += 1
                sheet.write_string(row_pos, 0, 'Current Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 1, float(data.get('current_balance')), tmp_style_num)
                row_pos += 1
                sheet.write_string(row_pos, 0, 'Net Cash Balance', tmp_style_num)
                sheet.write_number(row_pos, 1, float(data.get('ending_balance')), tmp_style_num)

    def _format_float_and_dates(self, currency_id, lang_id, formats):
        formats['line_header'].num_format = currency_id.excel_format
        formats['line_header_bold'].num_format = currency_id.excel_format
        formats['content_header_date'].num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

    def convert_to_date(self, datestring=False):
        lang = self.env.user.lang
        language_id = self.env['res.lang'].search([('code', '=', lang)], limit=1)
        if datestring:
            datestring = fields.Date.from_string(datestring).strftime(language_id.date_format)
            return datetime.strptime(datestring, language_id.date_format)
        else:
            return False

    def generate_xlsx_report(self, workbook, data, records):
        formats = self._define_formats(workbook)

        if not records:
            return False
        data = records.get_report_values()

        sheet = workbook.add_worksheet(data['form']['account_report_id'][1])
        sheet_2 = workbook.add_worksheet('Filters')

        sheet_2.set_column(0, 0, 25)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)
        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()

        lang = self.env.user.lang
        language_id = self.env['res.lang'].search([('code', '=', lang)], limit=1)
        self._format_float_and_dates(self.env.user.company_id.currency_id, language_id, formats)

        sheet.merge_range(0, 0, 0, 3, f"{data['form']['account_report_id'][1]} - {data['form']['company_id'][1]}", formats['format_title'])
        dateformat = self.env.user.lang

        self.prepare_report_filters(data, sheet_2, formats)
        self.prepare_report_contents(data, sheet, formats)
