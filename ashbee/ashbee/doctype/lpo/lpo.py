# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import money_in_words


class LPO(Document):
	def validate(self):
		self._calculate_totals()
		self._set_money_in_words()

	def _calculate_totals(self):
		totals = 0.0
		for item in self.items:
			totals = totals + (item.qty * item.rate)
		self.base_grand_total = totals
		self.grand_total = totals

	def _set_money_in_words(self):
		self.in_words = money_in_words(self.grand_total, self.currency)
		self.base_in_words = money_in_words(self.base_grand_total, self.currency)
