# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def get_labour_expenses(filters):
    return frappe.db.sql("""
        SELECT COALESCE(SUM(costing_amount), 0) AS labor_expenses
        FROM `tabTimesheet Detail`
        WHERE docstatus = 1
        AND project = %(project)s
        AND DATE(from_time) <= %(to_date)s
        AND DATE(to_time) >= %(from_date)s
    """, filters, as_dict=1)[0]


def get_consumed_material_cost(filters):
    return frappe.db.sql("""
        SELECT COALESCE(SUM(total_amount), 0) AS total_consumed_material_cost
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
    """, filters, as_dict=1)[0]


def get_central_allocations(filters):
    return frappe.db.sql("""
        SELECT
            COALESCE(SUM(cep.allocation), 0) AS central_expenses,
            COALESCE(SUM(cep.labor_allocation), 0) AS central_labour
        FROM `tabCentral Expense Project` cep
        INNER JOIN `tabCentral Expense`
        ON cep.parent = `tabCentral Expense`.name
        WHERE `tabCentral Expense`.docstatus = 1
        AND project = %(project)s
        AND from_date <= %(to_date)s
        AND to_date >= %(from_date)s
    """, filters, as_dict=1)[0]


def get_indirect_costs(filters):
    return frappe.db.sql("""
        SELECT COALESCE(SUM(item.allocated), 0) AS indirect
        FROM `tabIndirect Cost Item` item
        INNER JOIN `tabIndirect Cost`
        ON item.parent = `tabIndirect Cost`.name
        WHERE `tabIndirect Cost`.docstatus = 1
        AND project = %(project)s
        AND start_date <= %(to_date)s
        AND end_date >= %(from_date)s
    """, filters, as_dict=1)[0]


def get_direct_costs(filters):
    return frappe.db.sql("""
        SELECT 
            COALESCE(SUM(item.direct_cost), 0) AS material_direct,
            COUNT(*) AS qty
        FROM `tabDirect Cost Item` item
        INNER JOIN `tabDirect Cost`
        ON item.parent = `tabDirect Cost`.name
        WHERE `tabDirect Cost`.docstatus = 1
        AND job_no = %(project)s
        AND item.posting_date
        BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)[0]

