# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import math
import frappe
from frappe import _
from frappe.model.document import Document
from functools import reduce
from ashbee.utils import get_costs_by_projects


class IndirectCost(Document):
	def validate(self):
		self._set_fraction_total()
		if not self.items:
			filters = {
				'from_date': self.start_date,
				'to_date': self.end_date,
				'company': self.company,
			}

			projects = get_costs_by_projects(filters)

			if not projects:
				frappe.throw(_('No active projects found within the date range. If you have transactions, set the project as active.'))

			self._allocate_items(projects)
		else:
			self._check_allocation()

	def on_submit(self):
		self._update_project_indirect_cost()

	def on_cancel(self):
		self._update_project_indirect_cost(cancel=True)

	def _set_fraction_total(self):
		allocation = float(self.allocation or 0)
		fractional, rounded = math.modf(allocation)
		self.fraction_total = fractional

	def _allocate_items(self, projects):
		# Get the sum of all material issues
		total_mi_value = reduce(lambda x, y: x + y, projects.values())

		for project, mi_value in projects.items():
			allocated = self.allocation * (mi_value / total_mi_value)
			self.append('items', {
				'project': project,
				'allocated': allocated
			})

	def _check_allocation(self):
		total = reduce(lambda x, y: x + (y.allocated or 0), self.items, 0.00)

		if math.floor(total) != math.floor(self.allocation or 0):
			frappe.throw(_('Allocated values is not the same with allocated indirect expense'))

	def _update_project_indirect_cost(self, cancel=False):
		for item in self.items:
			total_indirect_cost = _get_total_cost(item.project, self.is_central)

			if cancel:
				new_total = total_indirect_cost - item.allocated
			else:
				new_total = total_indirect_cost + item.allocated

			_set_total_cost(item.project, new_total, self.is_central)

		frappe.db.commit()


def _get_total_cost(project, is_central):
	field = 'ashbee_total_central_cost' if is_central else 'ashbee_total_indirect_cost'
	return frappe.db.get_value('Project', project, field)


def _set_total_cost(project, total_cost, is_central):
	field = 'ashbee_total_central_cost' if is_central else 'ashbee_total_indirect_cost'
	frappe.db.set_value('Project', project, field, total_cost)
