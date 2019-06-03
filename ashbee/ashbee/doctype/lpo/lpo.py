# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import money_in_words


class LPO(Document):
	def validate(self):
		self._set_taxes_and_charges()
		self._calculate_taxes_and_charges()
		self._calculate_totals()
		self._set_money_in_words()

	def _set_taxes_and_charges(self):
		if self.taxes:
			self.taxes = []

		filters = {'parent': self.taxes_and_charges}
		taxes_and_charges = frappe.get_all('Purchase Taxes and Charges', filters=filters, fields=['*'])
		for taxes_and_charge in taxes_and_charges:
			taxes_and_charge.name = None
			self.append('taxes', taxes_and_charge)

	def _calculate_taxes_and_charges(self):
		tax_amount = 0.0
		for tax in self.taxes:
			tax_amount = tax_amount + tax.tax_amount
		self.base_taxes_and_charges_added = tax_amount
		self.base_total_taxes_and_charges = self.base_taxes_and_charges_added + self.base_taxes_and_charges_deducted
		self.taxes_and_charges_added = tax_amount
		self.total_taxes_and_charges = self.taxes_and_charges_added + self.base_taxes_and_charges_deducted

	def _calculate_totals(self):
		totals = 0.0
		for item in self.items:
			totals = totals + (item.qty * item.rate)
		self.base_grand_total = totals + self.base_total_taxes_and_charges
		self.grand_total = totals + self.total_taxes_and_charges

	def _set_money_in_words(self):
		self.in_words = money_in_words(self.grand_total, self.currency)
		self.base_in_words = money_in_words(self.base_grand_total, self.currency)
