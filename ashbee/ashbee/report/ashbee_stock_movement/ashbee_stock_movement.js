// Copyright (c) 2016, 9t9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ashbee Stock Movement"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname": "voucher_no",
			"label": __("Voucher #"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		}
	]
}
