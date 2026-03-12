# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
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
    _name = "emp.payslip.report"

    file = fields.Binary("Download File")
    file_name = fields.Char(string="File Name")
    file_type = fields.Selection([('pdf', 'PDF'), ('xls', 'XLS')
                                  ], 'File Type', default="xls")
    
    
    
    
    def get_sum_of_values(self, name_test=False, a=[], mn={}):
        val = mn.get(name_test)
        if len(a) == len(val):
            return [sum(x) for x in zip(a, val)]
        else:
            return val
    

    def employee_payslip_xls(self):
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
            return self.env.ref('bi_employee_payslip_report.action_report_export_emp_payslip').report_action(self,data=datas)




        elif self.file_type == 'xls':
            name_of_file = 'Export Payslip Report.xls'
            file_path = 'Export Payslip Report' + '.xls'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            # workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet('Export Payslip Report')

            header_format = workbook.add_format(
                {'bold': True, 'valign': 'vcenter', 'font_size': 16, 'align': 'center'})
            title_format = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 14,
                 'bg_color': '#D8D8D8'})
            cell_wrap_format_bold = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12})  ##E6E6E6
            cell_wrap_format = workbook.add_format(
                {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'left', 'font_size': 12, 'align': 'center', 'text_wrap': True })  ##E6E6E6
            
            
            sub_cell_wrap_format_bold = workbook.add_format({'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12, 'text_wrap': True})
            
            worksheet.set_row(1, 30)  # Set row height
            worksheet.set_row(4, 50)
            
            # Merge Row Columns
            TITLEHEDER = 'Payslip Report'

            worksheet.set_column(0, 0, 3)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 3, 25)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 15, 20)

            worksheet.merge_range(1, 1, 1, 7, TITLEHEDER, header_format)
            rowscol = 1
            
            active_ids = self.env.context.get('active_ids', [])
            payslip_ids = self.env['hr.payslip'].browse(active_ids)
            
            worksheet.merge_range(3, 0, 4, 0, 'NO', cell_wrap_format_bold)
            worksheet.merge_range(3, 1, 4, 1, 'Payslip Ref', cell_wrap_format_bold)
            worksheet.merge_range(3, 2, 4, 2, 'Employee', cell_wrap_format_bold)
            worksheet.merge_range(3, 3, 4, 3, 'Designation', cell_wrap_format_bold)
            worksheet.merge_range(3, 4, 4, 4, 'Period', cell_wrap_format_bold)
            worksheet.merge_range(3, 5, 4, 5, 'Pay Rules', cell_wrap_format_bold)

            # worksheet.merge_range(3, 6, 4, 6, 'Basic Salary',sub_cell_wrap_format_bold)
            # worksheet.merge_range(3, 7, 4, 7, 'Food Allow.', cell_wrap_format_bold)
            # worksheet.merge_range(3, 8, 4, 8, 'Tell Allow.', cell_wrap_format_bold)
            # worksheet.merge_range(3, 9, 4, 9, 'Vehicle Allow.', cell_wrap_format_bold)
            # worksheet.merge_range(3, 10, 4, 10, 'Other Allow.', cell_wrap_format_bold)
            # worksheet.merge_range(3, 11, 4, 11, 'Total Allow.', cell_wrap_format_bold)
            # worksheet.merge_range(3, 12, 4, 12, 'Rate', cell_wrap_format_bold)
            # worksheet.merge_range(3, 13, 4, 13, 'NOT Rate', cell_wrap_format_bold)
            # worksheet.merge_range(3, 14, 4, 14, 'HOT Rate.', cell_wrap_format_bold)
            worksheet.merge_range(3,6,3,17, 'Contractual' , cell_wrap_format_bold)
            worksheet.write(4, 6, 'Basic Salary', sub_cell_wrap_format_bold)
            worksheet.write(4, 7, 'Food Allow.', sub_cell_wrap_format_bold)
            worksheet.write(4, 8, 'Tell Allow.', sub_cell_wrap_format_bold)
            worksheet.write(4, 9, 'Vehicle Allow.', sub_cell_wrap_format_bold)
            worksheet.write(4, 10, 'Other Allow.', sub_cell_wrap_format_bold)
            worksheet.write(4, 11, 'Total Cont. Amount', sub_cell_wrap_format_bold)
            worksheet.write(4, 12, 'Rate Dedn (365)', sub_cell_wrap_format_bold)
            worksheet.write(4, 13, 'Rate', sub_cell_wrap_format_bold)

            worksheet.write(4, 14, 'NOT Rate', sub_cell_wrap_format_bold)
            worksheet.write(4, 15, 'HOT Rate.', sub_cell_wrap_format_bold)
            worksheet.write(4, 16, 'W/D (c/d)', sub_cell_wrap_format_bold)
            worksheet.write(4, 17, 'Hours', sub_cell_wrap_format_bold)

            worksheet.merge_range(3, 18, 3, 22, 'Attendance / TS', cell_wrap_format_bold)
            worksheet.write(4, 18, 'Basic Hour', sub_cell_wrap_format_bold)
            worksheet.write(4, 19, 'NOT Hour', sub_cell_wrap_format_bold)
            worksheet.write(4, 20, 'HOT Hour', sub_cell_wrap_format_bold)
            worksheet.write(4, 21, 'Absent Hour', sub_cell_wrap_format_bold)
            worksheet.write(4, 22, 'Total Hour.', sub_cell_wrap_format_bold)



            
            #For the get Lables
            print(payslip_ids)
            dict = {}
            lines=[dict]
            category = []
            main_sub = []
            for payslip in payslip_ids:
                for line in payslip.line_ids:
                    subcategory = []
                    category_id = line.category_id
                    all_subcategory = self.env['hr.payslip.line'].search([('category_id', '=', category_id.id),('slip_id','=', payslip.id)])
                    if line.category_id.code not in category:
                        category.append(line.category_id.code)
                        if all_subcategory:
                            for i in all_subcategory:
                                subcategory.append(i.name)
                                main_sub.append(i.name)
                        dict[line.category_id.code] = subcategory
                    else:
                        remaining=[]
                        if all_subcategory:
                            for i in all_subcategory:
                                if i.name not in main_sub:
                                    remaining.append(i.name)
                        if remaining:
                            for i, j in dict.items():
                                if i == line.category_id.name:
                                    for r in remaining:
                                        main_sub.append(r)
                                        dict[i].append(r)
            
            #For Print the Lable 
            for line in lines:
                start_col = 23
                row = 3
                col = 23
                
                if 'BASIC' in line.keys():
                    val = len(line.get('BASIC'))
                    values = line.get('BASIC')
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Basic' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Basic',cell_wrap_format_bold)
                        start_col = start_col + 1
                        
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                
                if 'ALW' in line.keys():
                    val = len(line.get('ALW'))
                    values  = line.get('ALW')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Allowance' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Allowance',cell_wrap_format_bold)
                        start_col = start_col + 1
                        
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                
                if 'GROSS' in line.keys():
                    val = len(line.get('GROSS'))
                    values  = line.get('GROSS')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Gross' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Gross',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                        
                if 'DED' in line.keys():
                    val = len(line.get('DED'))
                    values  = line.get('DED')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Deduction' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                        
                    else:
                        worksheet.write(row,start_col,'Deduction',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                        
                         
                         
                if 'NET' in line.keys():
                    val = len(line.get('NET'))
                    values  = line.get('NET')
                   
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Net' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Net',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                       
                       
                       
            
            
            #For Print the values
            #For the get Values of lable
            main=[]
            final = []
            new = {}
            no = 1
            
            lable = lines[0]
            for payslip in payslip_ids:
                ###################################Work day calculation########################################
                c = calendar.Calendar()

                year = payslip.date_from.year
                month = payslip.date_from.month
                weekend = self.env['week.day']
                if payslip.contract_id.weekend_day:
                    weekend = payslip.contract_id.weekend_day
                else:
                    weekend=payslip.struct_id.weekend_day
                monthcal = c.monthdatescalendar(year, month)
                weekend_day =[]
                weekend_day.append(calendar.SUNDAY)
                for wd in weekend:
                    if wd.name == 'SATURDAY':
                        weekend_day.append(calendar.SATURDAY)
                    if wd.name == 'SUNDAY':
                        weekend_day.append(calendar.SUNDAY)
                    if wd.name == 'MONDAY':
                        weekend_day.append(calendar.MONDAY)
                    if wd.name == 'TUESDAY':
                        weekend_day.append(calendar.TUESDAY)
                    if wd.name == 'WEDNESDAY':
                        weekend_day.append(calendar.WEDNESDAY)
                    if wd.name == 'THURSDAY':
                        weekend_day.append(calendar.THURSDAY)
                    if wd.name == 'FRIDAY':
                        weekend_day.append(calendar.FRIDAY)
                # no_of_weekend=0
                # for week in monthcal:
                #     for day in week:
                #         if
                number_of_weekday = len([day for week in monthcal for day in week if \
                                         day.weekday() in weekend_day and \
                                         day.month == month])
                month_total_day=calendar.monthrange(year, month)
                work_day=month_total_day[1]-number_of_weekday
                ###################################Work day calculation########################################
                get_emp_not_hour=sum(self.env['hr.overtime.line'].search([('date','>=',payslip.date_from),('date','<=',payslip.date_to),('ot_type','=','not'),('employee_id','=',payslip.employee_id.id)]).mapped('number_of_hours'))
                get_emp_hot_hour=sum(self.env['hr.overtime.line'].search([('date','>=',payslip.date_from),('date','<=',payslip.date_to),('ot_type','=','hot'),('employee_id','=',payslip.employee_id.id)]).mapped('number_of_hours'))
                get_emp_absent=self.env['hr.leave'].search([('date_from','>=',payslip.date_from),('date_to','<=',payslip.date_to),('employee_id','=',payslip.employee_id.id)])
                total_absent_hour=0
                for abs in get_emp_absent:
                    absent_time=abs.number_of_days*8
                    total_absent_hour+=absent_time
                values = {}
                category = []
                not_category = []
                values['NO'] = no,
                values['Payslip_Ref'] = payslip.number or '',
                values['Employee'] = payslip.employee_id.name or '',
                values['Designation'] = payslip.employee_id.job_id.name or '',
                values['Period'] = str(payslip.date_from) +  '  to  ' +str(payslip.date_to),
                values['Payrules'] = payslip.employee_id.contract_id.structure_type_id.name or '',
                if payslip.employee_id.contract_id.wage_type=='monthly':
                    values['Basic_Sal'] = payslip.employee_id.contract_id.wage or 0,
                    # values['Basic_hour'] =payslip.sum_worked_hours or 0
                if payslip.employee_id.contract_id.wage_type=='hourly':
                    values['Basic_Sal'] = payslip.employee_id.contract_id.hourly_wage or 0,
                    # values['Basic_hour']=hourly_basic_hour or 0
                values['Food_Alw'] = payslip.employee_id.contract_id.food_allowance or 0,
                values['Tell_Alw'] = payslip.employee_id.contract_id.telephone_allowance or 0,
                values['Vehicle_Alw'] = payslip.employee_id.contract_id.vehicle_allowance or 0,
                values['Other_Alw'] = payslip.employee_id.contract_id.other_allowance or 0,
                values['Total_Alw'] = round(payslip.employee_id.contract_id.wage+payslip.employee_id.contract_id.food_allowance+\
                                  payslip.employee_id.contract_id.telephone_allowance+payslip.employee_id.contract_id.vehicle_allowance+payslip.employee_id.contract_id.other_allowance,2) or 0,
                values['Rate'] = payslip.employee_id.contract_id.salary_per_h or 0,
                values['Rate'] = payslip.employee_id.contract_id.salary_per_h or 0,
                # values['Not_Rate'] = payslip.struct_id.not_rate  or 0,
                values['Not_Rate'] = payslip.contract_id.not_rate if (payslip.contract_id.not_rate>0 and payslip.contract_id.not_rate!=payslip.struct_id.not_rate) else payslip.struct_id.not_rate ,
                # values['Hot_Rate'] = payslip.struct_id.hot_rate or 0,
                values['Hot_Rate'] = payslip.contract_id.hot_rate if (payslip.contract_id.hot_rate>0 and payslip.contract_id.hot_rate!=payslip.struct_id.hot_rate) else payslip.struct_id.hot_rate ,
                if payslip.employee_id.contract_id.wage_type == 'monthly':
                    values['Work_Day'] = work_day or 0,
                    values['Hours'] = work_day*8 or 0,
                    # values['Rate_Dedn']=round(values['Total_Alw'][0]/values['Hours'][0],2) or 0,
                    values['Rate_Dedn']=round(values['Total_Alw'][0]*12/365/8,2) or 0,
                if payslip.employee_id.contract_id.wage_type == 'hourly':
                    values['Work_Day'] = 0 or 0,
                    values['Hours'] = 0 or 0,
                    values['Rate_Dedn']=0 or 0,
                if payslip.employee_id.contract_id.wage_type=='monthly':
                    basic_hour=payslip.sum_worked_hours
                    values['Basic_hour'] =payslip.sum_worked_hours or 0,
                if payslip.employee_id.contract_id.wage_type=='hourly':
                    basic_hour =round(payslip.net_wage/payslip.employee_id.contract_id.hourly_wage,2)
                    values['Basic_hour']=round(payslip.net_wage/payslip.employee_id.contract_id.hourly_wage,2) or 0,
                values['Not_Hour'] = get_emp_not_hour or 0,
                values['Hot_Hour'] = get_emp_hot_hour or 0,
                values['Absent_Hour'] = total_absent_hour or 0,
                values['Total_Hour']=round(basic_hour+get_emp_not_hour+get_emp_hot_hour+total_absent_hour,2) or 0,
                lines = self.env['hr.payslip.line'].search([('slip_id','=', payslip.id)])
                all_category = lines.mapped('category_id.code')
                sub_categ = lines.mapped('name')
                temp = []
                for i , j in lable.items():
                    if i not in ['no', 'payslip_ref', 'employee', 'designation', 'period','Payrules','Basic_Sal','Food_Alw','Tell_Alw','Vehicle_Alw','Other_Alw','Total_Alw','Rate_Dedn','Rate','Not_Rate','Hot_Rate','Work_Day','Hours','Basic_hour','Not_Hour','Hot_Hour','Absent_Hour','Total_Hour']:
                        if i in all_category:
                            present_categ = []
                            for sub in j:
                                if sub in sub_categ:
                                    for line in lines:
                                        if sub == line.name:
                                            present_categ.append(line.total)
                                            temp.append(line.total)
                                else:
                                    present_categ.append(0.0)
                                    temp.append(0.0)
                            values[i] = present_categ
                        else:
                            not_present_categ = []
                            for k in j:
                                not_present_categ.append(0.0)
                                temp.append(0.0)
                            values[i] = not_present_categ    
                no = no + 1
                main.append(values)
            
            
            
            #For get the values
            end_row = row
            row = 6
            for value in main:
                col = 0
                row = row
                list = ['NO', 'Payslip_Ref', 'Employee', 'Designation', 'Period','Payrules','Basic_Sal','Food_Alw','Tell_Alw','Vehicle_Alw','Other_Alw','Total_Alw','Rate_Dedn','Rate','Not_Rate','Hot_Rate','Work_Day','Hours','Basic_hour','Not_Hour','Hot_Hour','Absent_Hour','Total_Hour', 'BASIC', 'ALW', 'GROSS', 'DED', 'NET']
                # list = ['NO', 'Payslip_Ref', 'Employee', 'Designation', 'Period','Payrules','Basic_Sal', 'ALW', 'GROSS', 'DED', 'NET']
                for l in list:
                    if l in value.keys():
                        data  = value.get(l)
                        for r in data:
                            worksheet.write(row,col, r, cell_wrap_format)
                            col+=1
                row+=1
                end_row = row
            
            
            #For Get the Total
            total_row = end_row + 1
            list = ['Basic_Sal','Food_Alw','Tell_Alw','Vehicle_Alw','Other_Alw','Total_Alw','Rate_Dedn','Rate','Not_Rate','Hot_Rate','Work_Day','Hours','Basic_hour','Not_Hour','Hot_Hour','Absent_Hour','Total_Hour','BASIC', 'ALW', 'GROSS', 'DED', 'NET']
            coln = 6
            for l in list:
                lst = []
                for mn  in main:
                    if l in mn.keys():
                        lst = self.get_sum_of_values(l, lst, mn)
                        
                for r in lst:
                    worksheet.write(total_row,coln, r, cell_wrap_format_bold)
                    coln +=1
            
            worksheet.merge_range(total_row, 3, total_row, 4, 'Total', cell_wrap_format_bold)

            workbook.close()
            export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
            # export_id = base64.b64encode(open(file_path, 'rb+').read())
            result_id = self.env['emp.payslip.report'].create({'file': export_id, 'file_name': name_of_file})
            return {
                'name': 'Export Payslip Report',
                'view_mode': 'form',
                'res_id': result_id.id,
                'res_model': 'emp.payslip.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
