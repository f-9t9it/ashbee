# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class DirectCost(Document):
	def validate(self):
		total_direct_cost = 0.00
		for item in self.items:
			item.posting_date = self.posting_date
			total_direct_cost = total_direct_cost + item.direct_cost
		self.total_direct_cost = total_direct_cost

	def on_submit(self):
		for item in self.items:
			total_direct_cost = _get_total_direct_cost(item.job_no)
			added_direct_cost = total_direct_cost + item.direct_cost

			_set_total_direct_cost(item.job_no, added_direct_cost)
			_create_central_entry(self.name, item)

		frappe.db.commit()

	def on_cancel(self):
		for item in self.items:
			total_direct_cost = _get_total_direct_cost(item.job_no)
			subtracted_direct_cost = total_direct_cost - item.direct_cost

			_set_total_direct_cost(item.job_no, subtracted_direct_cost)
			_cancel_central_entry(item)

		frappe.db.commit()


def _get_total_direct_cost(job_no):
	return frappe.db.get_value('Project', job_no, 'ashbee_total_direct_cost')


def _set_total_direct_cost(job_no, direct_cost):
	frappe.db.set_value('Project', job_no, 'ashbee_total_direct_cost', direct_cost)


def _create_central_entry(name, item):
	central_project = frappe.db.get_single_value('Ashbee Settings', 'central_project')

	if item.job_no != central_project:
		return

	central_entry = frappe.get_doc({
		'doctype': 'Central Entry',
		'voucher_type': 'Direct Cost',
		'voucher_no': name,
		'voucher_detail_no': item.name,
		'posting_date': item.posting_date,
		'allocation': item.direct_cost
	}).insert()

	central_entry.submit()

	frappe.db.set_value('Direct Cost Item', item.name, 'central_entry', central_entry.name)


def _cancel_central_entry(item):
	if not item.central_entry:
		return

	central_entry = frappe.get_doc('Central Entry', item.central_entry)
	central_entry.cancel()
