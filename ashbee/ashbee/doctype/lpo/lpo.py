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
		if not self.taxes_and_charges:
			return

		if self.taxes:
			self.taxes = []

		filters = {'parent': self.taxes_and_charges}
		taxes_and_charges = frappe.get_all('Purchase Taxes and Charges', filters=filters, fields=['*'])
		for taxes_and_charge in taxes_and_charges:
			taxes_and_charge.name = None
			self.append('taxes', taxes_and_charge)

	def _calculate_taxes_and_charges(self):
		taxes_and_charges_added = 0.00
		taxes_and_charges_deducted = 0.00

		for tax in self.taxes:
			if tax.add_deduct_tax == "Add":
				taxes_and_charges_added = taxes_and_charges_added + tax.tax_amount
			else:
				taxes_and_charges_deducted = taxes_and_charges_deducted + tax.tax_amount

		self.base_taxes_and_charges_added = taxes_and_charges_added
		self.base_taxes_and_charges_deducted = taxes_and_charges_deducted
		self.base_total_taxes_and_charges = self.base_taxes_and_charges_added - self.base_taxes_and_charges_deducted

		self.taxes_and_charges_added = self.base_taxes_and_charges_added
		self.taxes_and_charges_deducted = self.base_taxes_and_charges_deducted
		self.total_taxes_and_charges = self.base_total_taxes_and_charges

	def _calculate_totals(self):
		totals = 0.0

		for item in self.items:
			totals = totals + (item.qty * item.rate)

		self.base_grand_total = self.base_grand_total + self.base_total_taxes_and_charges
		self.grand_total = self.grand_total + self.total_taxes_and_charges

	def _set_money_in_words(self):
		self.in_words = money_in_words(self.grand_total, self.currency)
		self.base_in_words = money_in_words(self.base_grand_total, self.currency)
