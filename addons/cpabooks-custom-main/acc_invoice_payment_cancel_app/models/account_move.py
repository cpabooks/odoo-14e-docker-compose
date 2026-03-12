# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
	_inherit = "account.move"

	def button_cancels(self):
		for move in self:
			if self.company_id.invoice_opration_type == 'cancel':
				move.with_context(force_delete=True).button_cancel()
				if self.company_id.payment_opration_type == 'cancel':
					payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
					for payment in payment_ids:
						payment.button_cancels()
			if self.company_id.invoice_opration_type == 'draft':
				move.button_cancel()
				if self.company_id.payment_opration_type == 'draft':
					payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
					for payment in payment_ids:
						payment.button_cancels()
				move.with_context(force_delete=True).button_draft()

			if self.company_id.invoice_opration_type == 'delete':
				move.with_context(force_delete=True).write({'posted_before':False})
				move.with_context(force_delete=True).button_cancel()
				if self.company_id.payment_opration_type == 'delete':
					payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
					for payment in payment_ids:
						payment.button_cancels()
				move.with_context(force_delete=True).button_draft()


	def account_move_cancel(self):
		account_move_ids =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_move_ids:
			move.with_context(force_delete=True).button_cancel()
			if self.company_id.payment_opration_type == 'cancel':
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
			
	def account_move_draft(self):
		account_move_ids =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_move_ids:
			move.with_context(force_delete=True).button_cancel()
			if self.company_id.payment_opration_type == 'draft':
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
			move.with_context(force_delete=True).button_draft()
			
	def account_move_delete(self):
		account_move_ids =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_move_ids:
			move.with_context(force_delete=True).write({'posted_before':False})
			move.with_context(force_delete=True).button_cancel()
			if self.company_id.payment_opration_type == 'delete':
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
			move.with_context(force_delete=True).button_draft()
		account_move_ids.with_context(force_delete=True).unlink() 
