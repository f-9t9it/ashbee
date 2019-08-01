# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import groupby

from ashbee.helpers import round_off_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	if data:
		_fill_totals(data)

		round_off_rows(data, [
			'normal_cost',
			'ot1',
			'ot2',
			'absent',
			'total'
		])

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
			"width": 200
		},
		{
			"label": _("Basic"),
			"fieldtype": "Currency",
			"fieldname": "basic",
			"width": 80
		},
		{
			"label": _("Normal Hour"),
			"fieldtype": "Data",
			"fieldname": "normal_hours",
			"width": 50
		},
		{
			"label": _("Normal Amt"),
			"fieldtype": "Currency",
			"fieldname": "normal_cost",
			"width": 80
		},
		{
			"label": _("OT1 Hour"),
			"fieldtype": "Data",
			"fieldname": "ot1_hours",
			"width": 50
		},
		{
			"label": _("OT1 Amt"),
			"fieldtype": "Currency",
			"fieldname": "ot1",
			"width": 80
		},
		{
			"label": _("OT2 Hour"),
			"fieldtype": "Data",
			"fieldname": "ot2_hours",
			"width": 50
		},
		{
			"label": _("OT2 Amt"),
			"fieldtype": "Currency",
			"fieldname": "ot2",
			"width": 80
		},
		{
			"label": _("Absent Hour"),
			"fieldtype": "Data",
			"fieldname": "absent_hours",
			"width": 50
		},
		{
			"label": _("Absent Amt"),
			"fieldtype": "Currency",
			"fieldname": "absent",
			"width": 80
		},
		{
			"label": _("Total Hours"),
			"fieldtype": "Data",
			"fieldname": "total_hours",
			"width": 80
		},
		{
			"label": _("Total Amt"),
			"fieldtype": "Currency",
			"fieldname": "total",
			"width": 100
		}
	]


def get_data(filters):
	# calendar_days = date_diff(
	# 	filters.get('to_date'),
	# 	filters.get('from_date')
	# )
	# working_hours = (calendar_days + 1) * 8

	timesheets = frappe.db.sql("""
		SELECT
			employee, employee_name, 
			normal_hours, normal_cost,
			ot1_hours, ot1,
			ot2_hours, ot2,
			hourly_cost, status
		FROM `tabBulk Timesheet Details`
		WHERE 
			DATE(start_date_time) BETWEEN %(from_date)s AND %(to_date)s
			AND docstatus = 1
		ORDER BY idx
	""", filters, as_dict=1)

	timesheets_data = _sum_employee_timesheets(
		groupby('employee', timesheets)
	)

	basics = _get_employees_basic()

	# _fill_employees_absent(timesheets_data)
	_fill_employees_basic(timesheets_data, basics)
	_fill_employees_total(timesheets_data)

	return timesheets_data


def _get_employees_basic():
	basics = frappe.get_all('Salary Structure Assignment', fields=['employee', 'base'])
	return {basic['employee']: basic['base'] for basic in basics}


def _fill_employees_basic(timesheets, basics):
	for timesheet in timesheets:
		employee = timesheet.get('employee')
		timesheet['basic'] = basics.get(employee)


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


def _sum_employee_timesheets(employee_timesheets):
	sorted_keys = _get_sorted_keys(
		employee_timesheets.keys()
	)

	timesheets_data = []
	for employee in sorted_keys:
		timesheets = employee_timesheets[employee]

		timesheet_row = reduce(
			_sum_timesheets,
			timesheets,
			_new_timesheet_row()
		)

		first_timesheet = timesheets[0]

		timesheet_row['employee'] = first_timesheet.get('employee')
		timesheet_row['employee_name'] = first_timesheet.get('employee_name')

		timesheets_data.append(timesheet_row)

	return timesheets_data


def _get_sorted_keys(keys):
	number_keys = []
	letter_keys = []

	for key in keys:
		if key.isdigit():
			number_keys.append(int(key))
		else:
			letter_keys.append(key)

	number_keys = sorted(number_keys)
	letter_keys = sorted(letter_keys)

	def convert_to_str(row):
		return str(row)

	number_keys = map(
		convert_to_str,
		number_keys
	)

	return number_keys + letter_keys


def _sum_timesheets(_, timesheet):
	compute_fields = [
		'normal_hours',
		'ot1_hours',
		'ot2_hours',
		'normal_cost',
		'ot1',
		'ot2',
		'absent_hours',
		'absent'
	]

	if timesheet.status == 'Absent':
		timesheet['normal_hours'] = 0
		timesheet['absent_hours'] = 8
		timesheet['absent'] = 8 * timesheet.get('hourly_cost')

	for field in compute_fields:
		timesheet_value = timesheet.get(field) or 0
		_[field] = _.get(field) + timesheet_value

	return _


def _new_timesheet_row():
	return {
		'normal_hours': 0,
		'ot1_hours': 0,
		'ot2_hours': 0,
		'absent_hours': 0,
		'normal_cost': 0.00,
		'ot1': 0.00,
		'ot2': 0.00,
		'absent': 0.00
	}
