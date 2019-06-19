# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.report.stock_ledger.stock_ledger import get_items, get_sle_conditions

from ashbee.utils import get_color_variants


def execute(filters=None):
	columns = get_columns()
	items = get_items(filters)
	color_variants = get_color_variants()
	sl_entries = get_stock_ledger_entries(filters, items)

	data = []
	for sl_entry in sl_entries:
		color = None
		if sl_entry.item_code in color_variants.keys():
			color = color_variants[sl_entry.item_code]
		sl_entry.update({'variant_color': color})
		data.append(sl_entry)

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
					AND %(to_date)s {item_conditions} {sle_conditions}
				ORDER BY posting_date ASC, posting_time ASC, creation ASC
			""".format(item_conditions=item_conditions, sle_conditions=get_sle_conditions(filters)), filters, as_dict=1)


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 95},
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		{"label": _("Variant Colour"), "fieldname": "variant_color", "fieldtype": "Data", "width": 95},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 110},
		{"label": _("Voucher #"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 100},
		{"label": _("Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 50, "convertible": "qty"},
		{"label": _("Balance Qty"), "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 100, "convertible": "qty"}
	]
