# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import get_first_day, get_last_day
from ashbee.utils import get_costs_by_projects


class CentralEntry(Document):
	def validate(self):
		if not self.items:
			filters = {
				'from_date': get_first_day(self.posting_date),
				'to_date': get_last_day(self.posting_date)
			}

			projects = get_costs_by_projects(filters)

			if not projects:
				frappe.throw(_('No active projects found within the date range. If you have transactions, set the project as active.'))

			self._allocate_items(projects)

	def on_submit(self):
		_set_project_costing(self.items, self.voucher_type)

	def on_cancel(self):
		_set_project_costing(self.items, self.voucher_type, cancel=True)

	def _allocate_items(self, projects):
		total_mi_value = reduce(lambda x, y: x + y, projects.values())

		for project, mi_value in projects.iteritems():
			allocated = self.allocation * (mi_value / total_mi_value)
			self.append('items', {
				'project': project,
				'allocated': allocated
			})


def _set_project_costing(items, voucher_type, cancel=False):
	for item in items:
		value = _get_project_central_field_value(item.project, voucher_type)
		allocated = item.allocated if not cancel else -item.allocated
		_set_project_central_field_value(
			item.project,
			voucher_type,
			value + allocated
		)
	frappe.db.commit()


def _get_project_central_field_value(project, voucher_type):
	fields = {
		'Timesheet': 'ashbee_total_central_labor',
		'Stock Entry': 'ashbee_total_central_cost'
	}

	return frappe.db.get_value('Project', project, fields[voucher_type])


def _set_project_central_field_value(project, voucher_type, value):
	fields = {
		'Timesheet': 'ashbee_total_central_labor',
		'Stock Entry': 'ashbee_total_central_cost'
	}

	frappe.db.set_value('Project', project, fields[voucher_type], value)
