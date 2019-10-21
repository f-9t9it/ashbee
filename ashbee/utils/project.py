# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def get_labour_expenses(filters):
    return frappe.db.sql("""
        SELECT SUM(costing_amount) AS labor_expenses
        FROM `tabTimesheet Detail`
        WHERE docstatus = 1
        AND project = %(project)s
        AND DATE(from_time) <= %(to_date)s
        AND DATE(to_time) >= %(from_date)s
    """, filters, as_dict=1)[0]


def get_consumed_material_cost(filters):
    return frappe.db.sql("""
        SELECT SUM(total_amount) AS total_consumed_material_cost
        FROM `tabStock Entry`
        WHERE docstatus = 1
        AND project = %(project)s
        AND posting_date 
        BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)[0]


def get_purchase_cost(filters):
    return frappe.db.sql("""
        SELECT COALESCE(SUM(amount), 0) AS total_purchase_cost
        FROM `tabPurchase Invoice Item`
        INNER JOIN `tabPurchase Invoice`
        ON `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
        WHERE `tabPurchase Invoice`.docstatus = 1
        AND project = %(project)s
        AND posting_date
        BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)
