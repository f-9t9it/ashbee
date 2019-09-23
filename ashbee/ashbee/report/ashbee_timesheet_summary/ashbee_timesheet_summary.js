// Copyright (c) 2016, 9t9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ashbee Timesheet Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "calculate_hourly_by_days",
			"label": __("Calculate Hourly by Days"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "salary_structures_on_date",
			"label": __("Salary Structures On Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	]
}
