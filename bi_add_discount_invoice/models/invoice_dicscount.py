# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api

class AccountInvoiceReport(models.Model):
	_inherit = 'account.invoice.report'
	
	_depends = {
		'account.invoice.line': ['discount'],
	}

	invoice_discount = fields.Float('Discount',readonly=True)

	def _select(self):
		return super(AccountInvoiceReport, self)._select() + ", sub.invoice_discount "

	def _sub_select(self):
		return super(AccountInvoiceReport, self)._sub_select() + ", sum(ail.discount) AS invoice_discount"

	def _group_by(self):
		return super(AccountInvoiceReport, self)._group_by() + ", ail.discount"






