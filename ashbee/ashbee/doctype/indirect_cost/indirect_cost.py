# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IndirectCost(Document):
	def validate(self):
		if not self.items:
			self._allocate_items()

	def on_submit(self):
		self._update_project_indirect_cost()

	def on_cancel(self):
		self._update_project_indirect_cost(cancel=True)

	def _update_project_indirect_cost(self, cancel=False):
		for item in self.items:
			total_indirect_cost = _get_total_indirect_cost(item.project)

			if cancel:
				new_total = total_indirect_cost - item.allocated
			else:
				new_total = total_indirect_cost + item.allocated

			_set_total_indirect_cost(item.project, new_total)

		frappe.db.commit()

	def _allocate_items(self):
		projects = _get_active_projects(self.start_date, self.end_date)
		allocation = self.indirect_expense / len(projects)

		for project in projects:
			self.append('items', {
				'project': project,
				'allocated': allocation
			})


def _get_total_indirect_cost(project):
	return frappe.db.get_value('Project', project, 'ashbee_total_indirect_cost')


def _set_total_indirect_cost(project, total_indirect_cost):
	frappe.db.set_value('Project', project, 'ashbee_total_indirect_cost', total_indirect_cost)


def _get_active_projects(start_date, end_date):
	return frappe.db.sql_list("""
		SELECT name FROM `tabProject`
		WHERE is_active='Yes'
	""")
