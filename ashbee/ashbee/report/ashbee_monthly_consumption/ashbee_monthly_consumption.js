// Copyright (c) 2016, 9t9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ashbee Monthly Consumption"] = {
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
          "fieldname": "warehouse",
          "label": __("Warehouse"),
          "fieldtype": "Link",
          "options": "Warehouse",
          "reqd": 1
      },
	]
}
