# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from ashbee.utils import create_central_entry


class AshbeeSettings(Document):
	def create_central_entries(self):
		frappe.msgprint('Generating Central Entries...')
		enqueue(_generate_central_entries, queue='default', timeout=6000, doc=self)


def _generate_central_entries(doc):
	filters = {
		'docstatus': 1,
		'ashbee_central_entry': '',
		'purpose': 'Material Issue',
		'project': doc.central_project
	}

	fields = ['name', 'posting_date', 'total_amount']

	material_issues = frappe.get_all('Stock Entry', filters=filters, fields=fields)

	for material_issue in material_issues:
		central_entry = create_central_entry(material_issue)
		central_entry.submit()

		stock_entry = material_issue.get('name')

		frappe.db.set_value('Stock Entry', stock_entry, 'ashbee_central_entry', central_entry.name)

	frappe.db.commit()
	frappe.publish_realtime(
		event='msgprint',
		message='Successfully generated Central Entries.',
		user=frappe.session.user
	)
