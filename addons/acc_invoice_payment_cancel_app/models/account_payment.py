# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPayment(models.Model):
	_inherit = "account.payment"

	def button_cancels(self):
		for payment in self:
			if self.company_id.payment_opration_type == 'cancel':
				payment.action_cancel()
			if self.company_id.payment_opration_type == 'draft':
				payment.action_cancel()
				payment.action_draft()
			if self.company_id.payment_opration_type == 'delete':
				payment.action_cancel()
				payment.action_draft()
				payment.sudo().unlink()

	def account_payment_cancel(self):
		payment_ids =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in payment_ids:
			payment.action_cancel()
			
	def account_payment_draft(self):
		payment_ids =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in payment_ids:
			payment.action_cancel()
			payment.action_draft()
			
	def account_payment_delete(self):
		payment_ids =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in payment_ids:
			payment.action_cancel()
			payment.action_draft()
		payment_ids.sudo().unlink()