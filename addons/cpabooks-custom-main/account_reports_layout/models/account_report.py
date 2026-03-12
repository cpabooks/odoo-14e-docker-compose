import io
from collections import OrderedDict

import xlsxwriter
from odoo import models, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    # def _get_table(self, options, excel_report=False):
    #     headers, lines = self.get_header(options), self._get_lines(options)
    #
    #     def get_name(inp):
    #         return inp.split(' (')[0]
    #
    #     if excel_report:
    #         new_items = []
    #         line_map = {}
    #         line_column_map = {}
    #
    #         new_ind = 0
    #
    #         for ind, line in enumerate(lines):
    #             name = get_name(line['name'])
    #             if name in line_map:
    #                 line_column_map[name]['columns'] = line_column_map[name]['columns'] + line['columns']
    #             else:
    #                 new_ind += 1
    #                 line_map[name] = new_ind
    #                 line_column_map[name] = line
    #
    #         line_map_sorted = OrderedDict(sorted(line_map.items(), key=lambda item: item[1]))
    #
    #         for key, value in line_map_sorted.items():
    #             # print(key, value)
    #             new_items.append(line_column_map[key])
    #
    #         lines = new_items
    #
    #     return headers, lines, excel_report

    def _get_table(self, options, excel_report=False):
        headers, lines = self.get_header(options), self._get_lines(options)

        def get_name(inp):
            return inp.split(' (')[0]

        if excel_report:
            new_items = []
            line_map = {}
            line_column_map = {}

            new_ind = 0

            for ind, line in enumerate(lines):
                name = get_name(line['name'])
                if name in line_map:
                    line_column_map[name]['columns'] = line_column_map[name]['columns'] + line['columns']
                else:
                    new_ind += 1
                    line_map[name] = new_ind
                    line_column_map[name] = line

            line_map_sorted = OrderedDict(sorted(line_map.items(), key=lambda item: item[1]))

            for key, value in line_map_sorted.items():
                # print(key, value)
                new_items.append(line_column_map[key])

            lines = new_items

        return headers, lines, excel_report  # Return the excel_report argument as well

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        headers, lines = self.with_context(
            no_format=True, print_mode=True, prefetch_fields=False)._get_table(options, excel_report=True)

        header_aug = headers[0][1]
        header_tax_name = header_aug['name'].replace('Balance', 'Tax')

        # header_aug_tax = {
        #     'class': header_aug['class'],
        #     'name': header_tax_name
        #     # 'style': header_aug['style']
        # }
        # headers[0].append(header_aug_tax)

        # Add headers.
        for header in headers:
            x_offset = 0
            for column in header:
                column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ').replace(
                    ' \n ', ' ')
                colspan = column.get('colspan', 1)
                if colspan == 1:
                    sheet.write(y_offset, x_offset, column_name_formated, title_style)
                else:
                    sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated,
                                      title_style)
                x_offset += colspan
            y_offset += 1

        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value,
                                         date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file


class AccountAccountingReport(models.AbstractModel):
    _inherit = 'account.accounting.report'

    def _format_line(self, value_dict, value_getters, value_formatters, current, options, total=False):
        """Build the report line based on the position in the report.

        Basic informations such as id, parent_id, unfoldable, unfolded, level are set here
        but this should be overriden to customize columns, the name and other specific fields
        in each report.
        :param value_dict (dict): the result of the read_group
        :param value_getters (list<function>): list of getter to retrieve each column's data.
            The parameter passed to the getter is the result of the read_group
        :param value_formatters (list<functions>): list of the value formatters.
            The parameter passed to the setter is the result of the getter.
        :param current (list<tuple>): list of tuple(grouping_key, id)
        :param options (dict): report options
        :param total (bool): set to True for section totals
        :return dict: the report line
        """
        id = self._build_line_id(current)
        hierarchy_detail = self._get_hierarchy_details(options)[len(current) - 1]
        res = {
            'id': id,
            'parent_id': self._build_parent_line_id(current) or None,
            'unfolded': ((id in options.get('unfolded_lines', []))
                         or options.get('unfold_all')
                         or self._context.get('print_mode')),
            'unfoldable': hierarchy_detail.foldable,
            'level': len(current),
            'colspan': hierarchy_detail.namespan,
            'columns': [
                {'name': v, 'no_format': v}
                for v, formatter in zip(
                    [getter(value_dict) for getter in value_getters],
                    value_formatters,
                )
            ],
            'class': 'total' if len(current) == 0 else '',
        }
        if getattr(self, '_format_all_line', None):
            self._format_all_line(res, value_dict, options)
        format_func = None
        if current:
            res[current[-1][0]] = current[-1][1]
            format_func = getattr(self, '_format_%s_line' % current[-1][0])
        else:
            format_func = getattr(self, '_format_total_line', None)
        if format_func:
            format_func(res, value_dict, options)
        if total:
            res['name'] = _('Total %s') % res['name']
        res['columns'] = res['columns'][hierarchy_detail.namespan - 1:]

        return res



