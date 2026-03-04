# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models
import xlwt
import base64
from io import BytesIO
import html2text
from datetime import datetime


class CrmLeadDetailExcelExtended(models.Model):
    _name = "crm.lead.detail.excel.extended"
    _description = 'Excel Entries Extended'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)

    def download_report(self):

        return{
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=crm.lead.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (self.id, self.file_name),
            'target': 'new',
        }


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_crm_lead_xls_entry(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sh_print_lead.sh_crm_lead_details_report_wizard_form_action')
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'crm.lead'
        action['context'] = ctx
        return action


class ShCrmLeadDetailsReportWizard(models.TransientModel):
    _name = "sh.crm.lead.details.report.wizard"
    _description = 'Crm Lead details report wizard model'

    def print_crm_lead_entries_xls_report(self):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center, vertical center;borders:top thick;borders:bottom thick;')
        format1 = xlwt.easyxf('font:bold True;align: horiz left')
        format2 = xlwt.easyxf(
            'font:bold True;align: horiz center;pattern: pattern solid, fore_colour gray25;')

        data = {}
        data = dict(data or {})
        active_ids = self.env.context.get('active_ids')

        crm_lead = self.env['crm.lead'].search(
            [('id', 'in', active_ids)])

        handle = html2text.HTML2Text()
        NO = 0
        for record in crm_lead:
            NO+=1
            meeting_lines = []
            order_lines = []
            final_value = {}

            final_value['name'] = record.name
            if record.partner_id :
                final_value['partner_id'] = record.partner_id.name
            else:    
                final_value['partner_id'] = ''    
            if record.email_from:
                final_value['email_from'] = record.email_from
            else:    
                final_value['email_from'] = '' 
            if record.phone:
                final_value['phone'] = record.phone
            else:    
                final_value['phone'] = ''   
            if record.mobile:     
                final_value['mobile'] = record.mobile
            else:    
                final_value['mobile'] = ''
            if record.website:
                final_value['website'] = record.website
            else:
                final_value['website'] = ''
            if record.partner_name:
                final_value['partner_name'] = record.partner_name
            else:
                final_value['partner_name'] = ''
            if record.user_id:
                final_value['user_id'] = record.user_id.name
            else:
                final_value['user_id'] = ''    
            if record.title:
                final_value['title'] = record.title
            else:
                final_value['title'] = ''
            if record.contact_name:
                final_value['contact_name'] = record.contact_name
            else:    
                final_value['contact_name'] = ''
            if record.function:
                final_value['function'] = record.function
            else:
                final_value['function'] = ''
            if record.team_id.name:    
                final_value['team_id'] = record.team_id.name
            else:
                final_value['team_id'] =  ''  
            if record.expected_revenue:      
                final_value['expected_revenue'] = record.expected_revenue
            else:
                final_value['expected_revenue'] = ''    
            if record.probability:    
                final_value['probability'] = record.probability
            else:
                final_value['probability'] = ''
            if record.date_deadline:
                final_value['date_deadline'] = datetime.strftime(record.date_deadline, "%d/%m/%Y") 
            else:
                final_value['date_deadline'] = ''        
            if record.campaign_id:
                final_value['campaign_id'] = record.campaign_id.name
            else:
                final_value['campaign_id'] = ''
            if record.medium_id:
                final_value['medium_id'] = record.medium_id.name    
            else:
                final_value['medium_id'] = ''
            if record.source_id:    
                final_value['source_id'] = record.source_id.name
            else:
                final_value['source_id'] = ''    
            if record.referred:
                final_value['referred'] = record.referred
            else:
                final_value['referred'] = ''

            priority = ''
            if record.priority == '0':
                priority = str('Low')
            elif record.priority == '1':
                priority = str('Medium')
            elif record.priority == '2':
                priority = 'High'
            elif record.priority == '3':
                priority = 'Very High'

            final_value['description'] = ''
            if record.description:
                final_value['description'] = handle.handle(record.description)

            for meetings in record.calendar_meeting_ids:
                product = {
                    'name': meetings.name,
                    'start': datetime.strftime(meetings.start, "%d/%m/%Y"),
                    'stop': datetime.strftime(meetings.stop, "%d/%m/%Y"),
                    'location': meetings.location,
                    'duration': meetings.duration,
                }

                if meetings.partner_ids:
                    pp = []
                    for pr_id in meetings.partner_ids:
                        pp.append(pr_id.name)
                    product['partner_ids'] = pp

                meeting_lines.append(product)

            for sale in record.sale_quotation_ids:
                product = {
                    'name': sale.name,
                    'date_order': datetime.strftime(sale.date_order, "%d/%m/%Y"),
                    'partner_id': sale.partner_id.name,
                    'user_id': sale.user_id.name,
                    'amount_total': sale.amount_total,
                    'state': sale.state,
                }

                order_lines.append(product)

            Name = 'Sheet ' + str(NO)+ ' - ' + str(record.name)
            worksheet = workbook.add_sheet(
                str(Name), cell_overwrite_ok=True)
            
            if record.type == 'lead' or record.type == False:
                name = 'Leads # ' + str(record.name)
            elif record.type == 'opportunity':
                name = 'Opportunity # ' + str(record.name)

            worksheet.write_merge(
                0, 1, 1, 6, name, heading_format)

            worksheet.col(0).width = int(5 * 260)
            worksheet.col(1).width = int(22 * 260)
            worksheet.col(2).width = int(30 * 260)
            worksheet.col(3).width = int(22 * 260)
            worksheet.col(4).width = int(30 * 260)
            worksheet.col(5).width = int(25 * 260)

            worksheet.write(3, 1, "Customer :", format1)
            worksheet.write(3, 2, final_value['partner_id'])
            worksheet.write(3, 4, "Email :", format1)
            if final_value['email_from']:
                worksheet.write(3, 5, final_value['email_from'])

            worksheet.write(4, 1, "Phone", format1)
            worksheet.write(4, 2, final_value['phone'])
            worksheet.write(4, 4, "Mobile", format1)
            worksheet.write(4, 5, final_value['mobile'])

            worksheet.write(5, 1, "Website", format1)
            worksheet.write(5, 2, final_value['website'])
            worksheet.write(5, 4, "Company Name", format1)
            worksheet.write(5, 5, final_value['partner_name'])

            worksheet.write(6, 1, "Salesperson", format1)
            worksheet.write(6, 2, final_value['user_id'])
            worksheet.write(6, 4, "Contact Name", format1)
            name = ''
            if record.title:
                name += record.title
            if record.contact_name:
                name += record.contact_name
            if record.function:
                name += '( ' + str(record.function) + ' )'
            worksheet.write(6, 5, name)

            worksheet.write(7, 1, "Sales Channel :", format1)
            worksheet.write(7, 2, final_value['team_id'])
            worksheet.write(7, 4, "Address :", format1)

            row = 7
            address = ''
            if record.street:
                address = str(record.street) + ' '
                worksheet.write(row, 5, address)
                row += 1
            if record.street2:
                address = str(record.street2) + ' '
                worksheet.write(row, 5, address)
                row += 1
            if record.city:
                address = str(record.city) + ' '
                worksheet.write(row, 5, address)
                row += 1
            if record.state_id:
                address = str(record.state_id.name) + ' '
                worksheet.write(row, 5, address)
                row += 1
            if record.zip:
                address = str(record.zip) + ' '
                worksheet.write(row, 5, address)
                row += 1
            if record.country_id:
                address = str(record.country_id.name) + ' '
                worksheet.write(row, 5, address)
                row += 1

            if record.type == 'opportunity':

                worksheet.write(row, 1, "Expected Revenue :", format1)
                worksheet.write(row, 2, str(final_value['expected_revenue']))
                worksheet.write(row, 4, "Probability :", format1)
                worksheet.write(row, 5, str(final_value['probability'])+'%')
                row += 1

            worksheet.write(row, 1, "Priority : ", format1)
            worksheet.write(row, 2, priority)
            worksheet.write(row, 4, "Expected Closing :", format1)
            worksheet.write(row, 5, str(final_value['date_deadline']))

            row += 3

            worksheet.write_merge(
                row, row+1, 1, 6, 'Marketing Details', heading_format)
            row += 3
            worksheet.write(row, 1, "Campaign", format2)
            worksheet.write(row, 2, "Medium", format2)
            worksheet.write(row, 3, "Source", format2)
            worksheet.write(row, 4, "Referred By", format2)
            row += 1
            worksheet.write(row, 1, final_value['campaign_id'])
            worksheet.write(row, 2, final_value['medium_id'])
            worksheet.write(row, 3, final_value['source_id'])
            worksheet.write(row, 4, final_value['referred'])
            row += 2

            if meeting_lines:

                worksheet.write_merge(
                    row, row+1, 1, 6, 'Meeting Details', heading_format)
                row += 3
                worksheet.write(row, 1, "Subject", format2)
                worksheet.write(row, 2, "Start Date", format2)
                worksheet.write(row, 3, "End Date", format2)
                worksheet.write(row, 4, "Attendees", format2)
                worksheet.write(row, 5, "Location", format2)
                worksheet.write(row, 6, "Duration", format2)
                row += 1

                for rec in meeting_lines:

                    if rec.get('name'):
                        worksheet.write(row, 1, rec.get('name'))
                    if rec.get('start'):
                        worksheet.write(row, 2, str(rec.get('start')))
                    if rec.get('stop'):
                        worksheet.write(row, 3, str(rec.get('stop')))
                    if rec.get('partner_ids'):
                        worksheet.write(row, 4, ",".join(
                            rec.get('partner_ids')))
                    if rec.get('location'):
                        worksheet.write(row, 5, rec.get('location'))
                    if rec.get('duration'):
                        worksheet.write(row, 6, str(rec.get('duration')))

                    row += 1

            if order_lines:
                worksheet.write_merge(
                    row, row+1, 1, 6, 'Quotation Details', heading_format)
                row += 3
                worksheet.write(row, 1, "Sale Order", format2)
                worksheet.write(row, 2, "Order Date", format2)
                worksheet.write(row, 3, "Customer", format2)
                worksheet.write(row, 4, "Salesperson", format2)
                worksheet.write(row, 5, "Total", format2)
                worksheet.write(row, 6, "State", format2)
                row += 1

                for rec in order_lines:

                    if rec.get('name'):
                        worksheet.write(row, 1, rec.get('name'))
                    if rec.get('date_order'):
                        worksheet.write(row, 2, str(rec.get('date_order')))
                    if rec.get('partner_id'):
                        worksheet.write(row, 3, rec.get('partner_id'))
                    if rec.get('user_id'):
                        worksheet.write(row, 4, rec.get('user_id'))
                    if rec.get('amount_total'):
                        worksheet.write(row, 5, str(rec.get('amount_total')))
                    if rec.get('state'):
                        worksheet.write(row, 6, str(rec.get('state')))

                    row += 1

            row += 1

            worksheet.write_merge(
                row, row+1, 1, 6, 'Internal Notes :', heading_format)
            row += 2
            worksheet.write_merge(row, row+5, 1, 6, final_value['description'])

        filename = ('Crm/Lead Detail Xls Report' + '.xls')
        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['crm.lead.detail.excel.extended'].sudo().create({
            'excel_file': base64.encodebytes(fp.getvalue()),
            'file_name': filename,
        })

        return{
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=crm.lead.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (export_id.id, export_id.file_name),
            'target': 'new',
        }
