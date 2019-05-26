# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file


class BulkTimesheetImport(Document):
	def on_submit(self):
		rows = read_xlsx_file_from_attached_file(file_id=self.import_file)
		entry = _create_entry(rows, self.posting_date)
		_set_bulk_timesheet(self.name, entry)
		frappe.db.commit()


def _set_bulk_timesheet(upload_name, entry_name):
	frappe.db.set_value('Bulk Timesheet Import', upload_name, 'bulk_timesheet_entry', entry_name)


def _create_entry(rows, posting_date):
	headers = rows[0]

	entry = frappe.new_doc('Bulk Timesheet Entry')
	entry.company = 'Ashbee'
	entry.posting_date = posting_date

	for row in rows[1:]:
		detail = {}
		for i, column in enumerate(row):
			detail.update({headers[i]: column})
		entry.append('details', detail)

	entry.insert()

	return entry.name
