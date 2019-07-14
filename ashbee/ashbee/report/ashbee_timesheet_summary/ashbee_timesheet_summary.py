# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import date_diff


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	if data:
		_fill_totals(data)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Emp No"),
			"fieldtype": "Link",
			"fieldname": "employee",
			"options": "Employee",
			"width": 80
		},
		{
			"label": _("Emp Name"),
			"fieldtype": "Data",
			"fieldname": "employee_name",
			"width": 250
		},
		{
			"label": _("Basic"),
			"fieldtype": "Currency",
			"fieldname": "basic",
			"width": 80
		},
		{
			"label": _("Rate 1 Hour"),
			"fieldtype": "Data",
			"fieldname": "normal_hours",
			"width": 120
		},
		{
			"label": _("Rate 1 Amt"),
			"fieldtype": "Currency",
			"fieldname": "normal_cost",
			"width": 120
		},
		{
			"label": _("Rate 1.25 Hour"),
			"fieldtype": "Data",
			"fieldname": "ot1_hours",
			"width": 120
		},
		{
			"label": _("Rate 1.25 Amt"),
			"fieldtype": "Currency",
			"fieldname": "ot1",
			"width": 120
		},
		{
			"label": _("Rate 1.5 Hour"),
			"fieldtype": "Data",
			"fieldname": "ot2_hours",
			"width": 120
		},
		{
			"label": _("Rate 1.5 Amt"),
			"fieldtype": "Currency",
			"fieldname": "ot2",
			"width": 120
		},
		{
			"label": _("Absent Hour"),
			"fieldtype": "Data",
			"fieldname": "absent_hours",
			"width": 120
		},
		{
			"label": _("Absent Amt"),
			"fieldtype": "Currency",
			"fieldname": "absent",
			"width": 120
		},
		{
			"label": _("Total Hours"),
			"fieldtype": "Data",
			"fieldname": "total_hours",
			"width": 140
		},
		{
			"label": _("Total Amt"),
			"fieldtype": "Currency",
			"fieldname": "total",
			"width": 140
		}
	]


def get_data(filters):
	calendar_days = date_diff(
		filters.get('to_date'),
		filters.get('from_date')
	)

	working_hours = (calendar_days + 1) * 8

	timesheets = frappe.db.sql("""
		SELECT
			employee, employee_name, 
			sum(normal_hours) as normal_hours, sum(normal_cost) as normal_cost,
			sum(ot1_hours) as ot1_hours, sum(ot1) as ot1,
			sum(ot2_hours) as ot2_hours, sum(ot2) as ot2,
			hourly_cost
		FROM `tabBulk Timesheet Details`
		WHERE 
			DATE(start_date_time) BETWEEN %(from_date)s AND %(to_date)s
			AND docstatus = 1
		GROUP BY employee
		ORDER BY idx
	""", filters, as_dict=1)

	basics = _get_employees_basic()

	_fill_employees_basic(timesheets, basics)
	_fill_employees_absent(timesheets, working_hours)
	_fill_employees_total(timesheets)

	return timesheets


def _get_employees_basic():
	basics = frappe.get_all('Salary Structure Assignment', fields=['employee', 'base'])
	return {basic['employee']: basic['base'] for basic in basics}


def _fill_employees_basic(timesheets, basics):
	for timesheet in timesheets:
		employee = timesheet.get('employee')
		timesheet['basic'] = basics.get(employee)


def _fill_employees_absent(timesheets, working_hours):
	for timesheet in timesheets:
		timesheet['absent_hours'] = timesheet.get('normal_hours') - working_hours
		timesheet['absent'] = timesheet.get('hourly_cost') * timesheet.get('absent_hours')


def _fill_employees_total(timesheets):
	for timesheet in timesheets:
		timesheet['total_hours'] = timesheet.get('normal_hours') + timesheet.get('ot1_hours') + timesheet.get('ot2_hours')
		timesheet['total'] = timesheet.get('normal_cost') + timesheet.get('ot1') + timesheet.get('ot2')


def _fill_totals(data):
	total_row = {
		'normal_hours': 0,
		'normal_cost': 0.00,
		'ot1_hours': 0,
		'ot1': 0.00,
		'ot2_hours': 0,
		'ot2': 0.00,
		'absent_hours': 0,
		'absent': 0.00,
		'total': 0.00
	}

	for row in data:
		for key, value in total_row.items():
			total_row[key] = value + row[key]

	data.append(total_row)
