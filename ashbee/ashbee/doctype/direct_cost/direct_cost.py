# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class DirectCost(Document):
	def on_submit(self):
		for item in self.items:
			total_direct_cost = _get_total_direct_cost(item.job_no)
			added_direct_cost = total_direct_cost + item.direct_cost
			_set_total_direct_cost(item.job_no, added_direct_cost)
		frappe.db.commit()

	def on_cancel(self):
		for item in self.items:
			total_direct_cost = _get_total_direct_cost(item.job_no)
			subtracted_direct_cost = total_direct_cost - item.direct_cost
			_set_total_direct_cost(item.job_no, subtracted_direct_cost)
		frappe.db.commit()


def _get_total_direct_cost(job_no):
	return frappe.db.get_value('Project', job_no, 'ashbee_total_direct_cost')


def _set_total_direct_cost(job_no, direct_cost):
	frappe.db.set_value('Project', job_no, 'ashbee_total_direct_cost', direct_cost)
