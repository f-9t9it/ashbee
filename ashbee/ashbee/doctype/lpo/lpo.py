# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class LPO(Document):
	def validate(self):
		self._calculate_totals()

	def _calculate_totals(self):
		totals = 0.0
		for item in self.items:
			totals = totals + (item.qty * item.rate)
		self.base_grand_total = totals
		self.grand_total = totals

