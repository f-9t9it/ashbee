# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import money_in_words


class LPO(Document):
	def validate(self):
		self._calculate_items_total()

		self.base_net_total = self.base_total
		self.net_total = self.total

		self._set_taxes_and_charges()
		self._calculate_taxes_and_charges()
		self._apply_discount()
		self._calculate_taxes_after_discount()
		self._calculate_totals()
		self._set_money_in_words()

	def _calculate_items_total(self):
		total_qty = 0
		total_amount = 0.00
		total_vat = 0.00

		for item in self.items:
			item.amount = item.qty * item.rate
			item.vat_amount = item.amount * (item.vat_percentage / 100.00)
			total_qty = total_qty + item.qty
			total_amount = total_amount + item.amount
			total_vat = total_vat + item.vat_amount

		self.total_qty = total_qty
		self.total = total_amount
		self.vat_total = total_vat
		self.net_total = total_amount
		self.base_total = total_amount
		self.base_net_total = total_amount

	def _calculate_taxes_after_discount(self):
		taxes_and_charges_added = 0.00
		taxes_and_charges_deducted = 0.00

		for tax in self.taxes:
			if tax.charge_type == "On Net Total":
				tax.tax_amount_after_discount_amount = self.net_total * (tax.rate / 100.00)
				tax.base_tax_amount_after_discount_amount = self.base_net_total * (tax.rate / 100.00)

			tax_amount_after_discount_amount = tax.tax_amount_after_discount_amount

			if tax.add_deduct_tax == "Add":
				taxes_and_charges_added = taxes_and_charges_added + tax_amount_after_discount_amount
			else:
				taxes_and_charges_deducted = taxes_and_charges_deducted - tax_amount_after_discount_amount

		self.base_taxes_and_charges_added = taxes_and_charges_added
		self.base_taxes_and_charges_deducted = taxes_and_charges_deducted
		self.base_total_taxes_and_charges = self.base_taxes_and_charges_added - self.base_taxes_and_charges_deducted

		self.taxes_and_charges_added = self.base_taxes_and_charges_added
		self.taxes_and_charges_deducted = self.base_taxes_and_charges_deducted
		self.total_taxes_and_charges = self.base_total_taxes_and_charges

	def _set_taxes_and_charges(self):
		if self.taxes_and_charges:
			if self.taxes:
				self.taxes = []
			filters = {'parent': self.taxes_and_charges}
			taxes_and_charges = frappe.get_all('Purchase Taxes and Charges', filters=filters, fields=['*'])
			for taxes_and_charge in taxes_and_charges:
				taxes_and_charge.name = None
				self.append('taxes', taxes_and_charge)

		for tax in self.taxes:
			if tax.charge_type == "Actual":
				tax.rate = 0.00

	def _calculate_taxes_and_charges(self):
		taxes_and_charges_added = 0.00
		taxes_and_charges_deducted = 0.00

		for tax in self.taxes:
			self._calculate_taxes(tax)
			self._calculate_taxes_total(tax)
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
		if self.additional_discount_percentage:
			discount_amount = self.total * (self.additional_discount_percentage / 100.00)
			self.net_total = self.total - discount_amount
			self.base_net_total = self.base_total - discount_amount
		else:
			self.base_net_total = self.base_total - self.discount_amount
			self.net_total = self.total - self.discount_amount

	def _set_money_in_words(self):
		self.in_words = money_in_words(self.grand_total, self.currency)
		self.base_in_words = money_in_words(self.base_grand_total, self.currency)

	def _calculate_taxes(self, tax):
		if tax.rate:
			tax.tax_amount = self.net_total * (tax.rate / 100.00)

	def _calculate_taxes_total(self, tax):
		tax.total = self.net_total + tax.tax_amount

	def _calculate_discount(self):
		total = 0.00

		if self.apply_discount_on == "Grand Total":
			total = self.total + self.total_taxes_and_charges
		elif self.apply_discount_on == "Net Total":
			total = self.total

		if not self.discount_amount:
			self.discount_amount = 0.00

		if self.additional_discount_percentage:
			self.discount_amount = total * (self.additional_discount_percentage / 100.00)
