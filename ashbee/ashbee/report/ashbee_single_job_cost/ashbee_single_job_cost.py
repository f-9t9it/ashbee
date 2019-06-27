# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from ashbee.helpers import new_column


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	return [
		new_column("Reference", "reference", "Data", 95),
		new_column("Date", "date", "Date", 95),
		new_column("Description", "description", "Data", 200)
	]


def get_data(filters):
	return []
