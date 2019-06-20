# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ashbee.utils import get_month_date_range

from toolz import partial


class CentralExpense(Document):
	def validate(self):
		self.items = []
		self.projects = []

		date_range = get_month_date_range(self.posting_date)
		central_entries = _get_central_entries(date_range)
		self._set_central_entries(central_entries)

	def _set_central_entries(self, central_entries):
		append_and_sum = partial(_append_and_sum, self)
		total_allocation = reduce(append_and_sum, central_entries, 0.00)
		self.total_allocation = total_allocation


def _get_central_entries(date_range):
	return frappe.db.sql("""
		SELECT name AS central_entry, voucher_type AS entry_type, allocation
		FROM `tabCentral Entry`
		WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
	""", date_range, as_dict=1)


def _append_and_sum(central_expense, x, y):
	"""
	Use central expense to append to the table,
	and summation of x and y (used for reduce)
	:param central_expense:
	:param x: total_allocation
	:param y: Central Entry
	:return: total_allocation
	"""
	central_expense.append('items', y)
	return x + y['allocation']
