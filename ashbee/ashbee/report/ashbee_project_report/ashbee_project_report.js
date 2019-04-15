// Copyright (c) 2016, 9t9IT and contributors
// For license information, please see license.txt
/* eslint-disable */


var months = "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember";

frappe.query_reports["Ashbee Project Report"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Select Fiscal Year"),
			"fieldtype": "Link",
			"options":"Fiscal Year",
			//"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"month",
			"label": __("Select Month"),
			"fieldtype": "Select",
			"options":months,
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
