from odoo import api, models, fields, _


class Statistics(models.Model):
    _name = 'cpabooks.statistics'
    _description = 'Cpabooks Statistics'

    name = fields.Char('Name')

    # SALES
    def quotation(self):
        return {
            'name': 'Quotations',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'group_by': ['date_order:year', 'date_order:month'],
            },
            'domain': [('state', '=', 'draft')]
        }

    def delivery(self):
        return {
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'group_by': ['scheduled_date:year', 'scheduled_date:month'],
            },
            'domain': [
                ('picking_type_id.code', '=', 'outgoing')
            ]
        }

    def invoices(self):
        return {
            'name': 'Invoices',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'default_move_type': 'out_invoice',
                'group_by': ['invoice_date:year', 'invoice_date:month'],
            },
            'domain': [
                ('move_type', '=', 'out_invoice'),
            ]
        }

    def receipt(self):
        return {
            'name': 'Receipt Vouchers',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
                'search_default_inbound_filter': 1,
                'default_move_journal_types': ('bank', 'cash'),
                'group_by': ['date:year', 'date:month'],
            },
            'domain': [('payment_type', '=', 'inbound'), ('partner_type', '=', 'customer')]
        }

    # BILLS
    def purchase(self):
        return {
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'group_by': ['date_order:year', 'date_order:month'],
            },
            'domain': [('state','in',('purchase', 'done'))]
        }


    def grn(self):
        return {
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'group_by': ['scheduled_date:year', 'scheduled_date:month'],
            },
            'domain': [
                ('picking_type_id.code', '=', 'incoming')
            ]
        }

    def bills(self):
        return {
            'name': 'Bills',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'default_move_type': 'in_invoice',
                'group_by': ['invoice_date:year', 'invoice_date:month'],
            },
            'domain': [
                ('move_type', '=', 'in_invoice'),
            ]
        }

    def payment(self):
        return {
            'name': 'Delivery Orders',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'search_default_outbound_filter': 1,
                'default_move_journal_types': ('bank', 'cash'),
                'group_by': ['date:year', 'date:month'],
            },
            'domain': [('payment_type', '=', 'outbound'), ('partner_type', '=', 'supplier')]
        }
