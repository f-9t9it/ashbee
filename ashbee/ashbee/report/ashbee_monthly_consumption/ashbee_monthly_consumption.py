# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from functools import reduce
from ashbee.helpers import new_column


def execute(filters=None):
	columns = _get_columns(filters)
	data = _get_data(filters)
	return columns, data


def _get_columns(filters):
	return [
		new_column("Opening Balance AF Start Date", "opening_balance", "Currency", 130),
		new_column("Purchase/Return", "purchase_return", "Currency", 130),
		new_column("Stock Issued", "stock_issued", "Currency", 130),
		new_column("Closing Stock", "closing_stock", "Currency", 130)
	]


def _get_data(filters):
	def make_data(data, row):
		purchase_return = data.get('purchase_return', 0.00)
		stock_issued = data.get('stock_issued', 0.00)
		total_amount = row.get('total_amount')
		if row.get('is_return'):
			purchase_return = purchase_return + total_amount
		else:
			stock_issued = stock_issued + total_amount
		data['purchase_return'] = abs(purchase_return)
		data['stock_issued'] = stock_issued
		return data

	se_data = reduce(
		make_data,
		frappe.db.sql("""
			SELECT 
				ashbee_is_return AS is_return,
				total_amount
			FROM `tabStock Entry`
			WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND from_warehouse = %(warehouse)s AND docstatus = 1
		""", filters, as_dict=1),
		{}
	)

	pr_data = reduce(
		make_data,
		frappe.db.sql("""
			SELECT
				1 as is_return,
				grand_total as total_amount
			FROM `tabPurchase Receipt`
			WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND set_warehouse = %(warehouse)s AND docstatus = 1
		""", filters, as_dict=1),
		{}
	)

	opening_se_data = reduce(
		make_data,
		frappe.db.sql("""
			SELECT 
				ashbee_is_return AS is_return,
				total_amount
			FROM `tabStock Entry`
	        WHERE posting_date < %(from_date)s
	        AND from_warehouse = %(warehouse)s AND docstatus = 1
		""", filters, as_dict=1),
		{}
	)

	opening_pr_data = reduce(
		make_data,
		frappe.db.sql("""
				SELECT
					1 as is_return,
					grand_total as total_amount
				FROM `tabPurchase Receipt`
				WHERE posting_date < %(from_date)s
				AND set_warehouse = %(warehouse)s AND docstatus = 1
			""", filters, as_dict=1),
		{}
	)

	return [
		_merge_closing_opening(
			_merge_dict([se_data, pr_data]),
			_merge_dict([opening_se_data, opening_pr_data])
		)
	]


def _merge_closing_opening(closing, opening):
	opening_balance = opening['purchase_return'] - opening['stock_issued']
	return {
		'opening_balance': opening_balance,
		'purchase_return': closing['purchase_return'],
		'stock_issued': closing['stock_issued'],
		'closing_stock': opening_balance + closing['purchase_return'] - closing['stock_issued']
	}


def _merge_dict(data):
	def make_data(rdata, row):
		for key, value in row.items():
			if key not in rdata:
				rdata[key] = value
			else:
				rdata[key] = rdata[key] + value
		return rdata
	return reduce(make_data, data, {})
