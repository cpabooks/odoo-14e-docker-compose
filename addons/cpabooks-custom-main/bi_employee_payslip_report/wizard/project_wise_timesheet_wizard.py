import base64
import calendar
from datetime import datetime,timedelta
from io import BytesIO

from odoo import models, fields

class ProjectMonthWizard(models.TransientModel):
    _name = 'project.month.wizard'
    _description = 'Project Month Wizard'

    project_id = fields.Many2one('project.project', string='Project')

    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Month', required=True,default=lambda self: self._get_previous_month())

    def _get_previous_month(self):
        today = datetime.now()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        return last_day_of_previous_month.strftime('%m')

    year = fields.Selection(
        [(str(year), str(year)) for year in range(2000, 2101)],
        string='Year',
        required=True,default=lambda self: str(datetime.now().year)
    )
    company_id=fields.Many2one('res.company',string="Company", default=lambda self:self.env.company.id)



    # def action_genarate_report(self):
    #     import xlsxwriter
    #     import base64
    #     from io import BytesIO
    #     import datetime
    #     import calendar
    #
    #     year = int(self.year)
    #     month = int(self.month)
    #     _, days_in_month = calendar.monthrange(year, month)
    #
    #     start_date = datetime.date(year, month, 1)
    #     end_date = datetime.date(year, month, days_in_month)
    #
    #     domain = [
    #         ('project_id', '=', self.project_id.id),
    #         ('date', '>=', start_date),
    #         ('date', '<=', end_date),
    #     ]
    #     lines = self.env['account.analytic.line'].search(domain)
    #
    #     # Group data by designation > employee > date
    #     data = {}
    #     for line in lines:
    #         employee_obj = line.employee_id
    #         employee_name = employee_obj.name or 'Unknown'
    #         designation = employee_obj.job_id.name if employee_obj.job_id else 'N/A'
    #         date = line.date
    #
    #         data.setdefault(designation, {})
    #         data[designation].setdefault(employee_name, {})
    #         data[designation][employee_name][date] = data[designation][employee_name].get(date, 0) + line.unit_amount
    #
    #     # Create Excel file
    #     output = BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     sheet = workbook.add_worksheet('Timesheet Report')
    #
    #     # Define formats
    #     title_format_left = workbook.add_format({'bold': True, 'font_size': 18, 'underline': 1, 'align': 'left'})
    #     title_format_right = workbook.add_format({'bold': True, 'font_size': 18, 'underline': 1, 'align': 'right'})
    #     bold_large = workbook.add_format({'bold': True, 'font_size': 18})
    #     bold_header = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1, 'align': 'center'})
    #     bold_format = workbook.add_format({'bold': True})
    #     grand_total_format = bold_header
    #     total_formate_right= workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1, 'align': 'right'})
    #
    #     right_align_format = workbook.add_format({'bold': True, 'font_size': 18, 'align': 'right'})
    #
    #     # Title
    #     sheet.merge_range('A1:E1', 'Monthly Timesheet', title_format_left)
    #     sheet.merge_range('T1:AF1', f"{self.env.company.name}", title_format_right)
    #     sheet.write('A2', f"Client Name: {self.project_id.partner_id.name}", bold_format)
    #     sheet.write('A3', f"Site/Project Name: {self.project_id.name}", bold_format)
    #     month_name = calendar.month_name[month]
    #     sheet.write('A4', f"Month containing: {month_name} {year}", bold_large)
    #
    #     # Header
    #     sheet.write(4, 0, 'Worker Name', bold_header)
    #     sheet.write(4, 1, 'Trade', bold_header)
    #     for day in range(1, days_in_month + 1):
    #         sheet.write(4, day + 1, f'{day:02d}', bold_header)
    #     sheet.write(4, days_in_month + 2, 'Total', bold_header)
    #
    #     # Day names row
    #     sheet.write(5, 0, '',bold_header)
    #     sheet.write(5, 1, '',bold_header)
    #     for day in range(1, days_in_month + 1):
    #         date_obj = datetime.date(year, month, day)
    #         sheet.write(5, day + 1, date_obj.strftime('%a'), bold_header)
    #     sheet.write(5, days_in_month + 2, '', bold_header)
    #
    #     row_idx = 6
    #     daily_totals = {day: 0 for day in range(1, days_in_month + 1)}
    #     grand_total = 0
    #
    #     for designation in sorted(data.keys()):
    #         designation_total = 0
    #
    #         for employee, times in data[designation].items():
    #             sheet.write(row_idx, 0, employee)
    #             sheet.write(row_idx, 1, designation)
    #
    #             row_total = 0
    #             for day in range(1, days_in_month + 1):
    #                 date = datetime.date(year, month, day)
    #                 hours = times.get(date, 0)
    #                 sheet.write(row_idx, day + 1, hours)
    #                 row_total += hours
    #                 daily_totals[day] += hours
    #             sheet.write(row_idx, days_in_month + 2, row_total, bold_format)
    #
    #             designation_total += row_total
    #             grand_total += row_total
    #             row_idx += 1
    #
    #         # Designation total row
    #         # sheet.merge_range(row_idx, 0, row_idx, 1, f'Total Hours Of - {designation}', grand_total_format)
    #         upto_col=1
    #         for day in range(1, days_in_month + 1):
    #             day_total = sum(data[designation][emp].get(datetime.date(year, month, day), 0)
    #                             for emp in data[designation])
    #             # sheet.write(row_idx, day + 1, day_total, grand_total_format)
    #             upto_col=day+1
    #         sheet.merge_range(row_idx, 0, row_idx, upto_col, f'Total Hours Of - {designation}', total_formate_right)
    #         sheet.write(row_idx, days_in_month + 2, designation_total, total_formate_right)
    #         row_idx += 1
    #
    #     # Grand Total row
    #     sheet.merge_range(row_idx, 0, row_idx, 1, 'Grand Total Hours', grand_total_format)
    #     for day in range(1, days_in_month + 1):
    #         sheet.write(row_idx, day + 1, daily_totals[day], total_formate_right)
    #     sheet.write(row_idx, days_in_month + 2, grand_total, total_formate_right)
    #
    #     # Leave 3 rows after grand total
    #     row_idx += 4
    #
    #     # Left side formatting (Prepared, Checked, Verified)
    #     upperline_format = workbook.add_format({'top': 1, 'bold': True})
    #
    #     sheet.merge_range(row_idx, 1,row_idx, 2, "Prepared By (Admin)", upperline_format)
    #     sheet.merge_range(row_idx + 2, 1,row_idx + 2, 2, "Checked By (Accounts)", upperline_format)
    #     sheet.merge_range(row_idx + 4, 1,row_idx + 4, 2, "Verified By (HR)", upperline_format)
    #
    #     # Right side formatting (Approved By, Client Name)
    #     right_col_start = 24  # Column 'Y' is index 24
    #
    #     sheet.write(row_idx, right_col_start, "Approved By Authorised", bold_format)
    #     sheet.write(row_idx + 2, right_col_start, f"{self.project_id.partner_id.name}", bold_format)
    #
    #     # Column sizing
    #     sheet.set_column(0, 0, 25)  # Worker Name
    #     sheet.set_column(1, 1, 20)  # Trade
    #     sheet.set_column(2, days_in_month + 2, 6)
    #
    #
    #
    #     workbook.close()
    #     output.seek(0)
    #
    #     file_data = base64.b64encode(output.read())
    #     output.close()
    #
    #     filename = f"Timesheet_{self.project_id.name}_{self.month}_{self.year}.xlsx"
    #     attachment = self.env['ir.attachment'].create({
    #         'name': filename,
    #         'type': 'binary',
    #         'datas': file_data,
    #         'res_model': 'project.month.wizard',
    #         'res_id': self.id,
    #         'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     })
    #
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'self',
    #     }

    def action_genarate_report(self):
        import xlsxwriter
        import base64
        from io import BytesIO
        import datetime
        import calendar

        year = int(self.year)
        month = int(self.month)
        _, days_in_month = calendar.monthrange(year, month)

        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, days_in_month)

        # Domain changes based on project_id presence
        domain = [
            ('date', '>=', start_date),
            ('date', '<=', end_date),
        ]
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))

        lines = self.env['account.analytic.line'].search(domain)

        # Group data differently based on project_id presence
        if self.project_id:
            # Original grouping (designation > employee > date)
            data = {}
            for line in lines:
                employee_obj = line.employee_id
                employee_name = employee_obj.name or 'Unknown'
                designation = employee_obj.job_id.name if employee_obj.job_id else 'N/A'
                date = line.date

                data.setdefault(designation, {})
                data[designation].setdefault(employee_name, {})
                data[designation][employee_name][date] = data[designation][employee_name].get(date,
                                                                                              0) + line.unit_amount
        else:
            # New grouping (project > designation > employee > date) with same structure
            data = {}
            for line in lines:
                project_name = line.project_id.name if line.project_id else 'No Project'
                employee_obj = line.employee_id
                employee_name = employee_obj.name or 'Unknown'
                designation = employee_obj.job_id.name if employee_obj.job_id else 'N/A'
                date = line.date

                data.setdefault(project_name, {})
                data[project_name].setdefault(designation, {})
                data[project_name][designation].setdefault(employee_name, {})
                data[project_name][designation][employee_name][date] = data[project_name][designation][
                                                                           employee_name].get(date,
                                                                                              0) + line.unit_amount

        # Create Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Timesheet Report')

        # Define formats (same as original)
        title_format_left = workbook.add_format({'bold': True, 'font_size': 18, 'underline': 1, 'align': 'left'})
        title_format_right = workbook.add_format({'bold': True, 'font_size': 18, 'underline': 1, 'align': 'right'})
        bold_large = workbook.add_format({'bold': True, 'font_size': 18})
        bold_header = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1, 'align': 'center'})
        bold_format = workbook.add_format({'bold': True})
        grand_total_format = bold_header
        total_formate_right = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1, 'align': 'right'})
        right_align_format = workbook.add_format({'bold': True, 'font_size': 18, 'align': 'right'})

        # Title
        sheet.merge_range('A1:E1', 'Monthly Timesheet', title_format_left)
        sheet.merge_range('T1:AF1', f"{self.env.company.name}", title_format_right)

        if self.project_id:
            sheet.write('A2', f"Client Name: {self.project_id.partner_id.name}", bold_format)
            sheet.write('A3', f"Site/Project Name: {self.project_id.name}", bold_format)
        else:
            sheet.write('A2', "All Projects Timesheet Summary", bold_format)

        month_name = calendar.month_name[month]
        sheet.write('A4', f"Month containing: {month_name} {year}", bold_large)

        # Header - add project column only when no project_id
        col = 0
        if not self.project_id:
            sheet.write(4, col, 'Project', bold_header)
            col += 1

        sheet.write(4, col, 'Worker Name', bold_header)
        sheet.write(4, col + 1, 'Trade', bold_header)

        for day in range(1, days_in_month + 1):
            sheet.write(4, col + 1 + day, f'{day:02d}', bold_header)
        sheet.write(4, col + 1 + days_in_month + 1, 'Total', bold_header)

        # Day names row
        row5_col = 0
        if not self.project_id:
            sheet.write(5, row5_col, '', bold_header)
            row5_col += 1

        sheet.write(5, row5_col, '', bold_header)
        sheet.write(5, row5_col + 1, '', bold_header)

        for day in range(1, days_in_month + 1):
            date_obj = datetime.date(year, month, day)
            sheet.write(5, row5_col + 1 + day, date_obj.strftime('%a'), bold_header)
        sheet.write(5, row5_col + 1 + days_in_month + 1, '', bold_header)

        row_idx = 6
        daily_totals = {day: 0 for day in range(1, days_in_month + 1)}
        grand_total = 0

        if self.project_id:
            # Original project-specific report logic
            for designation in sorted(data.keys()):
                designation_total = 0

                for employee, times in data[designation].items():
                    sheet.write(row_idx, 0, employee)
                    sheet.write(row_idx, 1, designation)

                    row_total = 0
                    for day in range(1, days_in_month + 1):
                        date = datetime.date(year, month, day)
                        hours = times.get(date, 0)
                        sheet.write(row_idx, day + 1, hours)
                        row_total += hours
                        daily_totals[day] += hours
                    sheet.write(row_idx, days_in_month + 2, row_total, bold_format)

                    designation_total += row_total
                    grand_total += row_total
                    row_idx += 1

                # Designation total row
                upto_col = 1
                for day in range(1, days_in_month + 1):
                    day_total = sum(data[designation][emp].get(datetime.date(year, month, day), 0)
                                    for emp in data[designation])
                    upto_col = day + 1
                sheet.merge_range(row_idx, 0, row_idx, upto_col, f'Total Hours Of - {designation}', total_formate_right)
                sheet.write(row_idx, days_in_month + 2, designation_total, total_formate_right)
                row_idx += 1
        else:
            # New all-projects report logic
            for project in sorted(data.keys()):
                if project=='BTC':
                    print('***')
                project_total = 0
                project_start_row = row_idx
                project_employee_count = 0

                for designation in sorted(data[project].keys()):
                    designation_total = 0
                    designation_start_row = row_idx

                    for employee, times in data[project][designation].items():
                        sheet.write(row_idx, 0, project)  # Project name in first column
                        sheet.write(row_idx, 1, employee)
                        sheet.write(row_idx, 2, designation)

                        row_total = 0
                        upto_col=2
                        for day in range(1, days_in_month + 1):
                            date = datetime.date(year, month, day)
                            hours = times.get(date, 0)
                            sheet.write(row_idx, 3 + day - 1, hours)
                            row_total += hours
                            daily_totals[day] += hours
                            upto_col=day+2
                        sheet.write(row_idx, 3 + days_in_month, row_total, bold_format)

                        designation_total += row_total
                        project_total += row_total
                        grand_total += row_total
                        row_idx += 1
                        project_employee_count += 1

                    # Designation total row
                    if designation_total > 0:
                        sheet.merge_range(
                            row_idx, 0, row_idx, upto_col,
                            f'Total Hours Of - {designation}',
                            total_formate_right
                        )
                        sheet.write(row_idx, 3 + days_in_month, designation_total, total_formate_right)
                        row_idx += 1

                # Project total row
                if project_total > 0:
                    sheet.merge_range(
                        row_idx, 0, row_idx, upto_col,
                        f'Total Hours For {project}',
                        total_formate_right
                    )
                    sheet.write(row_idx, 3 + days_in_month, project_total, total_formate_right)
                    row_idx += 1

                    # Merge project name cells only if we have multiple rows
                    # if project_employee_count > 1:
                    #     sheet.merge_range(
                    #         project_start_row, 0,
                    #         project_start_row + project_employee_count - 1, 0,
                    #         project,
                    #         workbook.add_format({
                    #             'align': 'center',
                    #             'valign': 'vcenter',
                    #             'border': 1
                    #         })
                    #     )

                # row_idx += 1  # Add extra space between projects

        # Grand Total row
        if self.project_id:
            sheet.merge_range(row_idx, 0, row_idx, 1, 'Grand Total Hours', grand_total_format)
            start_day_col = 2
        else:
            sheet.merge_range(row_idx, 0, row_idx, 2, 'Grand Total Hours', grand_total_format)
            start_day_col = 3

        for day in range(1, days_in_month + 1):
            sheet.write(row_idx, start_day_col + day - 1, daily_totals[day], total_formate_right)
        sheet.write(row_idx, start_day_col + days_in_month, grand_total, total_formate_right)

        # Leave 3 rows after grand total
        row_idx += 4

        # Left side formatting (Prepared, Checked, Verified)
        upperline_format = workbook.add_format({'top': 1, 'bold': True})

        sheet.merge_range(row_idx, 1, row_idx, 2, "Prepared By (Admin)", upperline_format)
        sheet.merge_range(row_idx + 2, 1, row_idx + 2, 2, "Checked By (Accounts)", upperline_format)
        sheet.merge_range(row_idx + 4, 1, row_idx + 4, 2, "Verified By (HR)", upperline_format)

        # Right side formatting (Approved By, Client Name)
        right_col_start = 24  # Column 'Y' is index 24

        sheet.write(row_idx, right_col_start, "Approved By Authorised", bold_format)
        if self.project_id:
            sheet.write(row_idx + 2, right_col_start, f"{self.project_id.partner_id.name}", bold_format)
        else:
            sheet.write(row_idx + 2, right_col_start, "All Projects", bold_format)

        # Column sizing
        if self.project_id:
            sheet.set_column(0, 0, 25)  # Worker Name
            sheet.set_column(1, 1, 20)  # Trade
            sheet.set_column(2, days_in_month + 2, 6)
        else:
            sheet.set_column(0, 0, 25)  # Project Name
            sheet.set_column(1, 1, 25)  # Worker Name
            sheet.set_column(2, 2, 20)  # Trade
            sheet.set_column(3, days_in_month + 3, 6)

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        output.close()

        if self.project_id:
            filename = f"Timesheet_{self.project_id.name}_{self.month}_{self.year}.xlsx"
        else:
            filename = f"All_Projects_Timesheet_{self.month}_{self.year}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': file_data,
            'res_model': 'project.month.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }




