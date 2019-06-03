# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Doc No"),
            "fieldname": "doc_no",
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 120
        },
        {
            "label": _("Job Code"),
            "fieldname": "job_code",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Job Name"),
            "fieldname": "job_name",
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Int",
            "width": 80
        }
    ]


def get_data(filters):
    import pprint
    data = []

    material_issues = _get_material_issues(filters)

    data = material_issues
    return data


def _get_sql_conditions(filters):
    conditions = []

    if filters.get('job_code'):
        conditions.append('`tabProject`.ashbee_project_code = %(job_code)s')

    if filters.get('item_code'):
        conditions.append('`tabStock Entry Detail`.item_code = %(item_code)s')

    if filters.get('stock_entry'):
        conditions.append('`tabStock Entry`.name = %(stock_entry)s')

    return ' AND '.join(conditions)


def _get_material_issues(filters):
    sql_conditions = _get_sql_conditions(filters)

    if sql_conditions:
        sql_conditions = 'AND {}'.format(sql_conditions)

    return frappe.db.sql("""
        SELECT 
            `tabStock Entry`.posting_date AS 'date', 
            `tabStock Entry`.name AS doc_no, 
            `tabProject`.ashbee_project_code AS job_code,
            `tabStock Entry`.project AS job_name,
            SUM(`tabStock Entry Detail`.qty) AS qty
        FROM `tabStock Entry Detail`
        INNER JOIN `tabStock Entry` ON `tabStock Entry Detail`.parent = `tabStock Entry`.name
        INNER JOIN `tabProject` on `tabStock Entry`.project = `tabProject`.name
        WHERE `tabStock Entry`.docstatus = 1
        {sql_conditions}
        AND `tabStock Entry`.purpose = 'Material Issue'
        AND `tabStock Entry`.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY `tabStock Entry`.name
        ORDER BY `tabStock Entry`.posting_date DESC
    """.format(sql_conditions=sql_conditions), filters, as_dict=1)

