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
			"fieldname": "working_hours",
			"label": __("Working Hours"),
			"fieldtype": "Int",
			"reqd": 1
		}
	]
}
