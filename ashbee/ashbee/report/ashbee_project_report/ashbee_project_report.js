// Copyright (c) 2016, 9t9IT and contributors
// For license information, please see license.txt
/* eslint-disable */


var months = "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember";

frappe.query_reports["Ashbee Project Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"overhead_percent",
			"label": __("Calculate Overhead Charge"),
			"fieldtype": "Percent",
			"default": 20
		},

	]
}
