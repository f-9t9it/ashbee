# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from functools import reduce
from ashbee.utils import get_costs_by_projects


class IndirectCost(Document):
	def validate(self):
		if not self.items:
			filters = {
				'from_date': self.start_date,
				'to_date': self.end_date
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

	def _allocate_items(self, projects):
		# Get the sum of all material issues
		total_mi_value = reduce(lambda x, y: x + y, projects.values())

		for project, mi_value in projects.iteritems():
			allocated = self.allocation * (mi_value / total_mi_value)
			self.append('items', {
				'project': project,
				'allocated': allocated
			})

	def _check_allocation(self):
		total = reduce(lambda x, y: x + y.allocated, self.items, 0.00)

		if total != self.allocation:
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


# def _sum_material_issues_by_projects(_, material_issues):
# 	"""
# 	A reducer; sum all project-related material issues.
# 	:param _: a reduced object
# 	:param material_issues: all material issues
# 	:return _: summed material i
# ssues group by projects
# 	"""
# 	project = material_issues['project']
# 	value = material_issues['total_outgoing_value']
#
# 	if project in _:
# 		_[project] = _[project] + value
# 	else:
# 		_.update({project: value})
#
# 	return _


# def _get_material_issues(start_date, end_date, is_central):
# 	"""
# 	Get all submitted Stock Entry material issues
# 	 with project where project is active
# 	:param start_date:
# 	:param end_date:
# 	:return: list
# 	"""
# 	return frappe.db.sql("""
# 		SELECT `tabStock Entry`.name, `tabStock Entry`.total_outgoing_value, project
# 		FROM `tabStock Entry`
# 		INNER JOIN `tabProject` ON `tabProject`.name = `tabStock Entry`.project
# 		WHERE `tabStock Entry`.posting_date BETWEEN %s AND %s
# 		AND `tabStock Entry`.purpose = 'Material Issue'
# 		AND `tabStock Entry`.docstatus = 1
# 		AND `tabProject`.is_active = 'Yes'
# 		AND `tabStock Entry`.ashbee_production_issue = %i
# 	""", (start_date, end_date, is_central), as_dict=1)
