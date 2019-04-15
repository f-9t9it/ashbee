# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BulkTimesheetEntry(Document):
	

	def get_employee_name(self):
		employee = frappe.get_doc("Employee", self.employee)
		return employee.employee_name

	def get_project_name(self):
		project = frappe.get_doc("Project",self.project)
		return project.name
