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
		new_column("Reference", "reference", "Data", 150),
		new_column("Date", "date", "Date", 95),
		new_column("Description", "description", "Data", 200),
		new_column("Income", "income", "Currency", 90),
		new_column("Qty", "qty", "Currency", 90),
		new_column("Rate", "rate", "Currency", 90),
		new_column("Material+Direct", "material_direct", "Currency", 120),
		new_column("Labor Expenses", "labor_expenses", "Currency", 120),
		new_column("Central", "central", "Currency", 120),
		new_column("Indirect", "indirect", "Currency", 120)
	]


def get_data(filters):
	data = []

	project_expenses = _get_project_expenses(filters)
	data.append({
		'material_direct': project_expenses['material'] + project_expenses['direct'],
		'labor_expenses': project_expenses['labor'],
		'central': project_expenses['central_labor'] + project_expenses['central_cost'],
		'indirect': project_expenses['indirect_cost']
	})

	entries = [
		_get_stock_ledger_entries(filters),
		_get_timesheet_details(filters)
	]

	for entry in entries:
		data.extend(entry)

	return data


def _get_project_expenses(filters):
	return frappe.db.sql("""
		SELECT 
			total_costing_amount AS labor,
			(ashbee_total_direct_cost + total_purchase_cost) AS direct,
			total_consumed_material_cost AS material,
			ashbee_total_central_cost AS central_cost,
			ashbee_total_central_labor AS central_labor,
			ashbee_total_indirect_cost AS indirect_cost
		FROM `tabProject`
		WHERE name=%(project)s
	""", filters, as_dict=1)[0]


def _get_stock_ledger_entries(filters):
	return frappe.db.sql("""
		SELECT 
			posting_date AS date, 
			voucher_no AS reference, 
			item_code AS description,
			valuation_rate AS rate,
			actual_qty AS qty
		FROM `tabStock Ledger Entry`
		WHERE project=%(project)s 
		AND posting_date BETWEEN %(from_date)s AND %(to_date)s
	""", filters, as_dict=1)


def _get_timesheet_details(filters):
	timesheet_details = frappe.db.sql("""
		SELECT sum(costing_amount) AS rate
		FROM `tabTimesheet Detail`
		WHERE project=%(project)s
		AND DATE(from_time) BETWEEN %(from_date)s AND %(to_date)s
	""", filters, as_dict=1)

	if timesheet_details:
		timesheet_detail = timesheet_details[0]
		timesheet_detail['description'] = '<b>Timesheet Cost</b>'

	return timesheet_details
