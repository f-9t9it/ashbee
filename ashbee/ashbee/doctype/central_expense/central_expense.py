# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ashbee.utils import get_costs_by_projects, get_month_date_range

from toolz import partial


class CentralExpense(Document):
	def validate(self):
		self.items = []
		self.projects = []

		date_range = get_month_date_range(self.posting_date)

		central_entries = _get_central_entries(date_range)
		self._set_central_entries(central_entries)

		projects = get_costs_by_projects(date_range)
		self._set_projects(projects)

	def _set_central_entries(self, central_entries):
		append_and_sum = partial(_append_and_sum_central_entry, self)
		allocation = reduce(append_and_sum, central_entries, {
			'labor_allocation': 0.00,
			'cost_allocation': 0.00
		})
		self.labor_allocation = allocation['labor_allocation']
		self.cost_allocation = allocation['cost_allocation']
		self.total_allocation = self.labor_allocation + self.cost_allocation

	def _set_projects(self, projects):
		total_cost = reduce(lambda x, y: x + y, projects.values())
		for project, cost in projects.iteritems():
			ratio = cost / total_cost
			allocation = self.total_allocation * ratio
			self.append('projects', {
				'project': project,
				'cost': cost,
				'ratio': ratio,
				'allocation': allocation
			})
		self.total_cost = total_cost


def _get_central_entries(date_range):
	return frappe.db.sql("""
		SELECT name AS central_entry, voucher_type AS entry_type, allocation
		FROM `tabCentral Entry`
		WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
	""", date_range, as_dict=1)


def _append_and_sum_central_entry(central_expense, x, y):
	"""
	Use central expense to append to the table,
	and summation of x and y (used for reduce)
	:param central_expense:
	:param x: allocation; labor and cost
	:param y: Central Entry
	:return: allocation
	"""
	central_expense.append('items', y)

	allocation = y['allocation']
	entry_type = y['entry_type']

	if entry_type == 'Stock Entry':
		labor_allocation = x['labor_allocation'] + allocation
		x['labor_allocation'] = labor_allocation
	elif entry_type == 'Timesheet':
		cost_allocation = x['cost_allocation'] + allocation
		x['cost_allocation'] = cost_allocation

	return x
