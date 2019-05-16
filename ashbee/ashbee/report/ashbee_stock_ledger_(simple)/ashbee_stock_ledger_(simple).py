# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	items = get_items(filters)
	data = get_stock_ledger_entries(filters, items)

	return columns, data


def get_stock_ledger_entries(filters, items):
	item_conditions = ''
	if items:
		item_conditions = 'AND sle.item_code in ({})' \
			.format(', '.join(['"{0}"'.format(i) for i in items]))

	return frappe.db.sql("""
				SELECT CONCAT_WS(" ", posting_date, posting_time) as date,
					item_code, warehouse, actual_qty, qty_after_transaction, voucher_type, voucher_no
				FROM `tabStock Ledger Entry` sle 
				WHERE company=%(company)s 
					AND posting_date BETWEEN %(from_date)s 
					AND %(to_date)s {item_conditions}
				ORDER BY posting_date ASC, posting_time ASC, creation ASC
			""".format(item_conditions=item_conditions), filters, as_dict=1)


def get_items(filters):
	items = []
	if filters.get("item_code"):
		items = frappe.db.sql_list("""SELECT name FROM `tabItem` item WHERE item.name=%(item_code)s""", filters)
	return items


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 95},
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 110},
		{"label": _("Voucher #"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 100},
		{"label": _("Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 50, "convertible": "qty"},
		{"label": _("Balance Qty"), "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 100, "convertible": "qty"}
	]
