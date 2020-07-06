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
		new_column("Project", "project", "Link", 130, "Project"),
		new_column("Opening Balance AF Start Date", "opening_balance", "Currency", 130),
		new_column("Purchase/Return", "purchase_return", "Currency", 130),
		new_column("Stock Issued", "stock_issued", "Currency", 130),
		new_column("Closing Stock", "closing_stock", "Currency", 130)
	]


def _get_data(filters):
	stock_entries = frappe.db.sql("""
		SELECT 
			ashbee_is_return AS is_return,
			total_amount,
			project
		FROM `tabStock Entry`
        WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
		AND from_warehouse = %(warehouse)s AND docstatus = 1
	""", filters, as_dict=1)

	by_projects = _reduce_by_project(stock_entries)
	data = _get_data_by_projects(by_projects)

	opening_stock_entries = frappe.db.sql("""
		SELECT 
			ashbee_is_return AS is_return,
			total_amount,
			project
		FROM `tabStock Entry`
        WHERE posting_date < %(from_date)s
        AND from_warehouse = %(warehouse)s AND docstatus = 1
	""", filters, as_dict=1)

	opening_by_projects = _reduce_by_project(opening_stock_entries)
	opening_data = _get_data_by_projects(opening_by_projects)

	return _merge_closing_opening(data, opening_data)


def _reduce_by_project(stock_entries):
	def make_data(by_projects, row):
		project = row.pop('project')
		if not project:
			project = 'Others'
		if project and (project not in by_projects):
			by_projects[project] = [row]
		else:
			by_projects[project].append(row)
		return by_projects
	return reduce(make_data, stock_entries, {})


def _get_data_by_projects(by_projects):
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

	data_by_projects = []
	for project, value in by_projects.items():
		project_data = reduce(make_data, value, {})
		data_by_projects.append({
			**project_data,
			'project': project,
			'closing_stock': project_data.get('purchase_return') - project_data.get('stock_issued')
		})

	return data_by_projects


def _merge_closing_opening(closing, opening):
	data = []
	for row in closing:
		opening_data = list(filter(lambda x: x['project'] == row['project'], opening))
		if opening_data:
			opening_data = opening_data[0]
			row['opening_balance'] = opening_data['purchase_return'] - opening_data['stock_issued']
		else:
			row['opening_balance'] = 0
		row['closing_stock'] = row['opening_balance'] + row['purchase_return'] - row['stock_issued']
		data.append(row)
	return data
