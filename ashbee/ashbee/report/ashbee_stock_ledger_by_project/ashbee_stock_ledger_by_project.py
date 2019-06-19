# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_data(filters):
	return []


def get_columns():
	return [
		_get_column("Date", "date", "Date", 95),
		_get_column("Item Code", "item_code", "Link", 130, options='Item'),
		_get_column("Item Name", "item_name", "Data", 130),
		_get_column("Variant Colour", "variant_color", "Data", 95),
		_get_column("Project Code", "project_code", "Data", 95),
		_get_column("Project Name", "project_name", "Link", 95, options='Project'),
		_get_column("Qty", "actual_qty", "Float", 50).update({'convertible': 'qty'}),
		_get_column("Balance Qty", "qty_after_transaction", "Float", 100).update({'convertible': 'qty'}),
		_get_column("Stock UOM", "stock_uom", "Link", 70, options='UOM')
	]


def _get_column(label, fieldname, fieldtype, width, options=None):
	column = {"label": _(label), "fieldname": fieldname, "fieldtype": fieldtype, "width": width}
	if options:
		column.update({'options': options})
	return column
