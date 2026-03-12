import calendar

from odoo import fields, models, api, _
from datetime import datetime
import xlsxwriter
import base64
import io
from io import BytesIO
import tempfile
import csv
from io import StringIO


class EmpPayslipReport(models.TransientModel):
    _name = "emp.wps.report"

    file = fields.Binary("Download File")
    file_name = fields.Char(string="File Name")
    file_type = fields.Selection([('xls', 'XLS')], 'File Type', default="xls")

    def employee_wps_xls(self):
        if self.file_type == 'pdf':
            self.ensure_one()
            [data] = self.read()
            active_ids = self.env.context.get('active_ids', [])
            payslip = self.env['hr.payslip'].browse(active_ids)
            datas = {
                'ids': active_ids,
                'model': 'emp.payslip.report ',
                'form': data
            }
            # return self.env.ref('bi_employee_payslip_report.action_report_export_emp_payslip').report_action(self,
            #                                                                                                  data=datas)
            return False




        elif self.file_type == 'xls':
            name_of_file = 'Export WPS Report.xls'
            file_path = 'Export WPS Report' + '.xls'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            # workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet('Export WPS Report')

            header_format = workbook.add_format(
                {'bold': True, 'valign': 'vcenter', 'font_size': 16, 'align': 'center'})
            title_format = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 14,
                 'bg_color': '#D8D8D8'})
            cell_wrap_format_bold = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12})  ##E6E6E6
            cell_wrap_format = workbook.add_format(
                {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'left', 'font_size': 12,
                 'align': 'center', 'text_wrap': True})  ##E6E6E6

            sub_cell_wrap_format_bold = workbook.add_format(
                {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12, 'text_wrap': True})

            worksheet.set_row(1, 30)  # Set row height
            worksheet.set_row(4, 50)

            # Merge Row Columns
            TITLEHEDER = 'WPS Report'

            worksheet.set_column(0, 0, 3)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 3, 25)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 15, 20)

            worksheet.merge_range(1, 1, 1, 10, TITLEHEDER, header_format)
            rowscol = 1

            active_ids = self.env.context.get('active_ids', [])
            payslip_ids = self.env['hr.payslip'].browse(active_ids)

            worksheet.merge_range(3, 0, 4, 0, 'NO', cell_wrap_format_bold)
            worksheet.merge_range(3, 1, 4, 1, 'Payslip Ref', cell_wrap_format_bold)
            worksheet.merge_range(3, 2, 4, 2, 'Employee', cell_wrap_format_bold)
            worksheet.merge_range(3, 3, 4, 3, 'Designation', cell_wrap_format_bold)
            # NEW
            worksheet.merge_range(3, 4, 4, 4, 'Salary Month', cell_wrap_format_bold)
            worksheet.merge_range(3, 5, 4, 5, 'Company MOL ID', cell_wrap_format_bold)
            worksheet.merge_range(3, 6, 4, 6, 'Agent Routing Code', cell_wrap_format_bold)
            worksheet.merge_range(3, 7, 4, 7, 'Bank A/C', cell_wrap_format_bold)
            worksheet.merge_range(3, 8, 4, 8, 'Emp MOL ID', cell_wrap_format_bold)
            worksheet.merge_range(3, 9, 4, 9, 'No. of Leave Days', cell_wrap_format_bold)
            worksheet.merge_range(3, 10, 4, 10, 'Fixed Amount', cell_wrap_format_bold) #wps
            worksheet.merge_range(3, 11, 4, 11, 'Variable Amount', cell_wrap_format_bold) #net-wps
            worksheet.merge_range(3, 12, 4, 12, 'Total', cell_wrap_format_bold)#NET Salary
            # NEW


            # worksheet.merge_range(3, 6, 3, 17, 'Contractual', cell_wrap_format_bold)
            # worksheet.write(4, 6, 'Basic Salary', sub_cell_wrap_format_bold)
            # worksheet.write(4, 7, 'Food Allow.', sub_cell_wrap_format_bold)
            # worksheet.write(4, 8, 'Tell Allow.', sub_cell_wrap_format_bold)
            # worksheet.write(4, 9, 'Vehicle Allow.', sub_cell_wrap_format_bold)
            # worksheet.write(4, 10, 'Other Allow.', sub_cell_wrap_format_bold)
            # worksheet.write(4, 11, 'Total Cont. Amount', sub_cell_wrap_format_bold)
            # worksheet.write(4, 12, 'Rate Dedn (365)', sub_cell_wrap_format_bold)
            # worksheet.write(4, 13, 'Rate', sub_cell_wrap_format_bold)
            #
            # worksheet.write(4, 14, 'NOT Rate', sub_cell_wrap_format_bold)
            # worksheet.write(4, 15, 'HOT Rate.', sub_cell_wrap_format_bold)
            # worksheet.write(4, 16, 'W/D (c/d)', sub_cell_wrap_format_bold)
            # worksheet.write(4, 17, 'Hours', sub_cell_wrap_format_bold)
            #
            # worksheet.merge_range(3, 18, 3, 22, 'Attendance / TS', cell_wrap_format_bold)
            # worksheet.write(4, 18, 'Basic Hour', sub_cell_wrap_format_bold)
            # worksheet.write(4, 19, 'NOT Hour', sub_cell_wrap_format_bold)
            # worksheet.write(4, 20, 'HOT Hour', sub_cell_wrap_format_bold)
            # worksheet.write(4, 21, 'Absent Hour', sub_cell_wrap_format_bold)
            # worksheet.write(4, 22, 'Total Hour.', sub_cell_wrap_format_bold)

            # For the get Lables
            # print(payslip_ids)
            # dict = {}
            # lines = [dict]
            # category = []
            # main_sub = []
            # for payslip in payslip_ids:
            #     for line in payslip.line_ids:
            #         subcategory = []
            #         category_id = line.category_id
            #         all_subcategory = self.env['hr.payslip.line'].search(
            #             [('category_id', '=', category_id.id), ('slip_id', '=', payslip.id)])
            #         if line.category_id.code not in category:
            #             category.append(line.category_id.code)
            #             if all_subcategory:
            #                 for i in all_subcategory:
            #                     subcategory.append(i.name)
            #                     main_sub.append(i.name)
            #             dict[line.category_id.code] = subcategory
            #         else:
            #             remaining = []
            #             if all_subcategory:
            #                 for i in all_subcategory:
            #                     if i.name not in main_sub:
            #                         remaining.append(i.name)
            #             if remaining:
            #                 for i, j in dict.items():
            #                     if i == line.category_id.name:
            #                         for r in remaining:
            #                             main_sub.append(r)
            #                             dict[i].append(r)

            # For Print the Lable
            # for line in lines:
            #     start_col = 23
            #     row = 3
            #     col = 23
            #
            #     if 'BASIC' in line.keys():
            #         val = len(line.get('BASIC'))
            #         values = line.get('BASIC')
            #         if val > 1:
            #             worksheet.merge_range(row, start_col, row, start_col + (val - 1), 'Basic',
            #                                   cell_wrap_format_bold)
            #             start_col = start_col + val
            #             for i in values:
            #                 worksheet.write(4, col, i, sub_cell_wrap_format_bold)
            #                 col += 1
            #         else:
            #             worksheet.write(row, start_col, 'Basic', cell_wrap_format_bold)
            #             start_col = start_col + 1
            #
            #             worksheet.write(4, col, values[0], sub_cell_wrap_format_bold)
            #             col += 1
            #
            #     if 'ALW' in line.keys():
            #         val = len(line.get('ALW'))
            #         values = line.get('ALW')
            #
            #         if val > 1:
            #             worksheet.merge_range(row, start_col, row, start_col + (val - 1), 'Allowance',
            #                                   cell_wrap_format_bold)
            #             start_col = start_col + val
            #             for i in values:
            #                 worksheet.write(4, col, i, sub_cell_wrap_format_bold)
            #                 col += 1
            #         else:
            #             worksheet.write(row, start_col, 'Allowance', cell_wrap_format_bold)
            #             start_col = start_col + 1
            #
            #             worksheet.write(4, col, values[0], sub_cell_wrap_format_bold)
            #             col += 1
            #
            #     if 'GROSS' in line.keys():
            #         val = len(line.get('GROSS'))
            #         values = line.get('GROSS')
            #
            #         if val > 1:
            #             worksheet.merge_range(row, start_col, row, start_col + (val - 1), 'Gross',
            #                                   cell_wrap_format_bold)
            #             start_col = start_col + val
            #             for i in values:
            #                 worksheet.write(4, col, i, sub_cell_wrap_format_bold)
            #                 col += 1
            #         else:
            #             worksheet.write(row, start_col, 'Gross', cell_wrap_format_bold)
            #             start_col = start_col + 1
            #             worksheet.write(4, col, values[0], sub_cell_wrap_format_bold)
            #             col += 1
            #
            #     if 'DED' in line.keys():
            #         val = len(line.get('DED'))
            #         values = line.get('DED')
            #
            #         if val > 1:
            #             worksheet.merge_range(row, start_col, row, start_col + (val - 1), 'Deduction',
            #                                   cell_wrap_format_bold)
            #             start_col = start_col + val
            #             for i in values:
            #                 worksheet.write(4, col, i, sub_cell_wrap_format_bold)
            #                 col += 1
            #
            #         else:
            #             worksheet.write(row, start_col, 'Deduction', cell_wrap_format_bold)
            #             start_col = start_col + 1
            #             worksheet.write(4, col, values[0], sub_cell_wrap_format_bold)
            #             col += 1
            #
            #     if 'NET' in line.keys():
            #         val = len(line.get('NET'))
            #         values = line.get('NET')
            #
            #         if val > 1:
            #             worksheet.merge_range(row, start_col, row, start_col + (val - 1), 'Net', cell_wrap_format_bold)
            #             start_col = start_col + val
            #             for i in values:
            #                 worksheet.write(4, col, i, sub_cell_wrap_format_bold)
            #                 col += 1
            #         else:
            #             worksheet.write(row, start_col, 'Net', cell_wrap_format_bold)
            #             start_col = start_col + 1
            #             worksheet.write(4, col, values[0], sub_cell_wrap_format_bold)
            #             col += 1

            # For Print the values
            # For the get Values of lable
            main = []
            final = []
            new = {}
            no = 1

            # lable = lines[0]
            lable=["No",""]
            for payslip in payslip_ids:
                ###################################leave  calculation########################################
                leaves = self.env['hr.leave'].sudo().search(
                    [('date_from','>=',payslip.date_from),('date_from','<=',payslip.date_to),('employee_id','=',payslip.employee_id.id),
                     ('holiday_status_id','in',self.env['hr.leave.type'].sudo().search([('type_for','in',('leave_with_pay','leave_with_out_pay'))]).ids)], order='date_from')
                sum_of_leave=0
                for l in leaves:
                    start_date=l.date_from.date()
                    end_date=l.date_to.date()
                    if l.date_from.date()<payslip.date_from:
                        start_date=payslip.date_from
                    if l.date_to.date()>payslip.date_to:
                        end_date=payslip.date_to
                    num_of_days=end_date-start_date
                    sum_of_leave+=num_of_days.days+1



                ###################################Work day calculation########################################

                get_emp_absent = self.env['hr.leave'].search(
                    [('date_from', '>=', payslip.date_from), ('date_to', '<=', payslip.date_to),
                     ('employee_id', '=', payslip.employee_id.id)])
                total_absent_hour = 0
                for abs in get_emp_absent:
                    absent_time = abs.number_of_days * 8
                    total_absent_hour += absent_time
                values = {}
                start_month = payslip.date_from.month
                values['NO'] = no,
                values['Payslip_Ref'] = payslip.number or '',
                values['Employee'] = payslip.employee_id.name or '',
                values['Designation'] = payslip.employee_id.job_id.name or '',
                # values['Salary_month'] = str(payslip.date_from) + '  to  ' + str(payslip.date_to),
                values['Salary_month'] = calendar.month_name[start_month],
                # values['Company_mol_id'] =  payslip.employee_id.company_id.company_mol_id or '',
                values['Company_mol_id'] = payslip.struct_id.company_mol_id or '',
                values['Agent_routing_code'] =  payslip.employee_id.agent_routing_code.code or '',
                values['Bank_ac'] =payslip.employee_id.bank_account_id.acc_number or '',
                values['Emp_mol_id'] = payslip.employee_id.emp_mol_id or '',
                values['No_of_leave_days'] = sum_of_leave or 0,

                if payslip.employee_id.contract_id.wage_type == 'monthly':
                    values['Fixed_amount'] = payslip.contract_id.wps_salary or 0,
                    values['Variable_amount'] = (payslip.employee_id.contract_id.wage - payslip.contract_id.wps_salary) or 0,
                    values['Total'] =  payslip.employee_id.contract_id.wage or 0,
                if payslip.employee_id.contract_id.wage_type == 'hourly':
                    basic_hour = round(payslip.net_wage / payslip.employee_id.contract_id.hourly_wage, 2)
                    values['Fixed_amount'] =  0,
                    values['Variable_amount'] = ((payslip.employee_id.contract_id.hourly_wage*basic_hour) - payslip.contract_id.wps_salary) or 0,
                    values['Total'] = (payslip.employee_id.contract_id.hourly_wage*basic_hour) or 0,


                no = no + 1
                main.append(values)

            # For get the values
            # end_row = row
            row = 6
            for value in main:
                col = 0
                row = row
                list = ['NO', 'Payslip_Ref', 'Employee', 'Designation', 'Salary_month', 'Company_mol_id', 'Agent_routing_code', 'Bank_ac',
                        'Emp_mol_id', 'No_of_leave_days', 'Fixed_amount', 'Variable_amount', 'Total']
                for l in list:
                    if l in value.keys():
                        data = value.get(l)
                        for r in data:
                            worksheet.write(row, col, r, cell_wrap_format)
                            col += 1
                row += 1
                end_row = row

            # For Get the Total
            total_row = end_row + 1
            # list = ['Basic_Sal', 'Food_Alw', 'Tell_Alw', 'Vehicle_Alw', 'Other_Alw', 'Total_Alw', 'Rate_Dedn', 'Rate',
            #         'Not_Rate', 'Hot_Rate', 'Work_Day', 'Hours', 'Basic_hour', 'Not_Hour', 'Hot_Hour', 'Absent_Hour',
            #         'Total_Hour', 'BASIC', 'ALW', 'GROSS', 'DED', 'NET']
            # coln = 6
            # for l in list:
            #     lst = []
            #     for mn in main:
            #         if l in mn.keys():
            #             lst = self.get_sum_of_values(l, lst, mn)
            #
            #     for r in lst:
            #         worksheet.write(total_row, coln, r, cell_wrap_format_bold)
            #         coln += 1
            #
            # worksheet.merge_range(total_row, 3, total_row, 4, 'Total', cell_wrap_format_bold)

            workbook.close()
            export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
            # export_id = base64.b64encode(open(file_path, 'rb+').read())
            result_id = self.env['emp.wps.report'].create({'file': export_id, 'file_name': name_of_file})
            return {
                'name': 'Export WPS Report',
                'view_mode': 'form',
                'res_id': result_id.id,
                'res_model': 'emp.wps.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }