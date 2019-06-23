# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import unique, compose, partial, merge

from ashbee.utils import get_color_variants


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_data(filters):
	sl_entries = _get_stock_ledger_entries(filters)

	get_projects = compose(
		merge,
		partial(map, _get_project_code),
		_extract_projects
	)

	set_project_code = partial(_set_project_code_field, get_projects(sl_entries))
	set_color = partial(_set_variant_color_field, get_color_variants())

	fill_sl_entries = compose(
		partial(map, set_color),
		partial(map, set_project_code)
	)

	return fill_sl_entries(sl_entries)


def get_columns():
	return [
		_get_column("Date", "date", "Date", 95),
		_get_column("Item Code", "item_code", "Link", 130, options='Item'),
		_get_column("Item Name", "item_name", "Data", 200),
		_get_column("Stock UOM", "stock_uom", "Link", 90, options='UOM'),
		_get_column("Variant Colour", "variant_color", "Data", 95),
		_get_column("Voucher #", "voucher_no", "Data", 95),
		_get_column("Project Code", "project_code", "Data", 95),
		_get_column("Project Name", "project_name", "Link", 95, options='Project'),
		_get_column("Qty", "actual_qty", "Float", 50),
		_get_column("Balance Qty", "qty_after_transaction", "Float", 100)

	]


def _set_variant_color_field(variant_colors, data):
	item_code = data['item_code']
	if item_code in variant_colors:
		variant_color = variant_colors[item_code]
		data['variant_color'] = variant_color
	return data


def _set_project_code_field(project_codes, data):
	project_name = data['project_name']
	if project_name in project_codes:
		project_code = project_codes[project_name]
		data['project_code'] = project_code
	return data


def _get_project_code(project):
	return {project: frappe.db.get_value('Project', project, 'ashbee_project_code')}


def _extract_projects(data):
	"""
	Get projects from entries
	:param data:
	:return:
	"""
	projects = compose(
		list,
		unique,
		partial(map, lambda x: x['project_name']),  # extract project name
		partial(filter, lambda x: x['project_name'])  # not empty
	)
	return projects(data)


def _get_stock_ledger_entries(filters):
	"""
	Get data from Stock Ledger Entries with the following fields:
	(1) date, (2) item_code, (3) actual_qty, (4) qty_after_transaction,
	(5) project, (6) stock_uom, (7) item_name
	:param filters:
	:return: Stock Ledger Entries
	"""
	return frappe.db.sql("""
		SELECT CONCAT_WS(" ", sle.posting_date, sle.posting_time) AS date,
			sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.project AS project_name,
			sle.stock_uom, item.item_name, sle.voucher_no
		FROM `tabStock Ledger Entry` sle
		INNER JOIN `tabItem` item ON sle.item_code = item.name
		WHERE sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
		ORDER BY sle.posting_date ASC, sle.posting_time ASC, sle.creation ASC
	""", filters, as_dict=1)


def _get_column(label, fieldname, fieldtype, width, options=None):
	column = {"label": _(label), "fieldname": fieldname, "fieldtype": fieldtype, "width": width}
	if options:
		column.update({'options': options})
	return column
