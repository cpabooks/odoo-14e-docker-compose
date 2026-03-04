# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError



class InvoiceAbstractReport(models.AbstractModel):
    """
    Abstract model for generating customer invoice reports,
    including invoice details, payments, and balances.
    """
    _name = 'report.tk_customer_statements.customer_report_template'
    _description = 'Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Retrieves customer invoice data for a specific partner within a given date range,
        calculates total amounts, payments, and balances, and provides relevant customer details.
        """
        return_data = {}
        company = self.env.company
        currency = company.currency_id.symbol
        print(data)
        start_date = data.get('form_data').get('start_date')
        end_date = data.get('form_data').get('end_date')
        partner_id = data.get('form_data').get('partner_id')
        inv_type = data.get('form_data').get('inv_type')
        start_date_obj = datetime.strptime(str(start_date), '%Y-%m-%d')
        start_date_format = start_date_obj.strftime('%d-%m-%Y')
        end_date_obj = datetime.strptime(str(end_date), '%Y-%m-%d')
        end_date_format = end_date_obj.strftime('%d-%m-%Y')
        if not inv_type:
            raise ValidationError(_("Please Enter PDF For"))

        #OPENING BALANCE SECTION

        partner=self.env['res.partner'].browse(partner_id[0])
        print(type(partner))
        print(partner)
        invoice_before_start = self.env['account.move'].search([
            ('invoice_date', '<', start_date),
            ('partner_id', '=', partner_id[0]),
            ('move_type', '=', inv_type)
        ], order="invoice_date asc")

        print([i.amount_residual for i in invoice_before_start])

        payment_before_start = self.env['account.payment'].search([
            ('date', '<', start_date),
            ('partner_id', '=', partner_id[0]),
        ])
        print([i.amount for i in payment_before_start])


        inv_amt = sum([inv.amount_total_signed for inv in invoice_before_start]) if invoice_before_start else 0.00
        pmt_amt = sum([pmt.amount for pmt in payment_before_start]) if payment_before_start else 0.0
        opening_balance = inv_amt - pmt_amt
        opening_start_date = invoice_before_start[0].invoice_date if invoice_before_start else ''
        opening_end_date = invoice_before_start[-1].invoice_date if invoice_before_start else ''

        #INVOICE SECTION
        invoices = self.env['account.move'].search([
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('partner_id', '=', partner_id[0]),
            ('move_type', '=', inv_type)
        ], order="invoice_date asc")

        invoice_data = []
        total_amount = 0
        total_payment = 0
        total_balance = 0
        payment_with_inv = []
        for invoice in invoices:
            paid_amount = invoice.amount_total - invoice.amount_residual
            payment_date = ''
            pay_term_lines = invoice.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
            for partial in pay_term_lines.matched_debit_ids:
                payment_with_inv.append(partial.debit_move_id.payment_id.id)
                payment_date = partial.debit_move_id.payment_id.date
            for partial in pay_term_lines.matched_credit_ids:
                payment_with_inv.append(partial.credit_move_id.payment_id.id)
                payment_date = partial.credit_move_id.payment_id.date

            inv_date = datetime.strptime(str(invoice.invoice_date ), '%Y-%m-%d') if invoice.invoice_date else False
            due_date = datetime.strptime(str(invoice.invoice_date_due ), '%Y-%m-%d') if invoice.invoice_date_due else False
            pmt_date = datetime.strptime(str(payment_date), '%Y-%m-%d') if payment_date else ''

            invoice_date = inv_date.strftime('%d-%m-%Y') if inv_date else ''
            inv_due_date = due_date.strftime('%d-%m-%Y') if due_date else ''
            payment_date = pmt_date.strftime('%d-%m-%Y') if pmt_date else ''


            invoice_info = {
                'invoice_date': invoice_date,
                'due_date': inv_due_date,
                'invoice_id': invoice.name,
                'partner': invoice.partner_id.name,
                'amount': round(invoice.amount_total, 2),
                'payment_amount': round(paid_amount, 2),
                'balance_due': round(invoice.amount_residual, 2),
                'payment_date': payment_date or ''
            }



            invoice_data.append(invoice_info)
            total_amount += invoice.amount_total
            total_payment += paid_amount
            total_balance += invoice.amount_residual

        return_data.update({
            'docs': invoice_data,
            'total_amount': round(total_amount, 2),
            'total_balance': round(total_balance, 2),
            'partner_name': partner_id[1],
            'partner_street': partner.street,
            'partner_street2': partner.street2,  # invoices[0].partner_id.street2
            'partner_zip': partner.zip,  # invoices[0].partner_id.zip
            'partner_city': partner.city,  # invoices[0].partner_id.city
            'partner_state_id': partner.state_id.name,  # invoices[0].partner_id.state_id.name
            'partner_country_id': partner.country_id.name,  # invoices[0].partner_id.country_id.name
            'today_date': date.today(),
            'currency': currency,
            'opening_balance': opening_balance,
            'opening_start_date': opening_start_date,
            'opening_end_date': opening_end_date,
            'start_date': start_date_format,
            'end_date': end_date_format
        })

        # PAYMENT SECTION
        payment_data = []
        payments = self.env['account.payment'].search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('partner_id', '=', partner_id[0]),
            ('id', 'not in', payment_with_inv)
        ], order='date asc')

        for payment in payments:
            pmt_date = datetime.strptime(str(payment.date), '%Y-%m-%d') if payment.date else ''
            payment_date = pmt_date.strftime('%d-%m-%Y') if pmt_date else ''
            payment_info = {
                'payment_date': payment_date,
                'payment': payment.name or '',
                'amount': payment.amount or 0.0
            }
            total_payment += payment.amount
            payment_data.append(payment_info)
        return_data.update({
            'payments': payment_data,
            'total_inv_payment': round(total_payment, 2),

        })

        refund_data = []
        ref_type = "in_refund" if inv_type == "in_invoice" else "out_refund"
        refunds = self.env['account.move'].search([
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('partner_id', '=', partner_id[0]),
            ('move_type', '=', ref_type)
        ], order="invoice_date asc")
        for refund in refunds:
            ref_date = datetime.strptime(str(refund.invoice_date), '%Y-%m-%d') if refund.invoice_date else False
            refund_date = ref_date.strftime('%d-%m-%Y') if ref_date else ''
            refund_info = {
                'refund_date': refund_date,
                'refund_id': refund.name,
                'amount': refund.amount_total
            }

            refund_data.append(refund_info)
        if refund_data:
            return_data.update({
                'refunds': refund_data
            })
        return return_data
