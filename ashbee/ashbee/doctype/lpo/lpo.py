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
		self._apply_discount()
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
			self._calculate_taxes(tax)
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
		self.base_grand_total = self.base_net_total + self.base_total_taxes_and_charges
		self.grand_total = self.net_total + self.total_taxes_and_charges

	def _apply_discount(self):
		self._calculate_discount()
		if self.apply_discount_on == 'Net Total':
			self.net_total = self.total - self.discount_amount
			self.base_net_total = self.base_total - self.discount_amount
		else:
			self.grand_total = self.net_total - self.discount_amount
			self.base_grand_total = self.base_net_total - self.discount_amount

	def _set_money_in_words(self):
		self.in_words = money_in_words(self.grand_total, self.currency)
		self.base_in_words = money_in_words(self.base_grand_total, self.currency)

	def _calculate_taxes(self, tax):
		if tax.rate:
			tax.tax_amount = self.net_total * (tax.rate / 100.00)

	def _calculate_discount(self):
		if not self.discount_amount:
			self.discount_amount = 0.00

		if self.additional_discount_percentage:
			self.discount_amount = self.total * (self.additional_discount_percentage / 100.00)
