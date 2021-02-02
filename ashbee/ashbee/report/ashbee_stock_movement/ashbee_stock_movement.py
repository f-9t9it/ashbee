# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.stock.report.stock_ledger.stock_ledger import get_sle_conditions
from toolz import unique, compose, partial, merge

from ashbee.utils import get_color_variants
from ashbee.helpers import new_column


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_data(filters):
    sl_entries = _get_stock_ledger_entries(filters)
    if not sl_entries:
        return []

    get_projects = compose(
        merge,
        partial(map, _get_project_code),
        _extract_projects,
    )

    projects = get_projects(sl_entries)
    color_variants = get_color_variants()

    make_data = compose(
        list,
        partial(
            map,
            lambda x: merge(
                x,
                {
                    "project_code": projects.get(x.get("project_name")),
                    "variant_color": color_variants.get(x.get("item_code")),
                },
            ),
        ),
    )

    return make_data(sl_entries)


def get_columns():
    return [
        new_column("Date", "date", "Date", 95),
        new_column("Item Code", "item_code", "Link", 130, options="Item"),
        new_column("Item Name", "item_name", "Data", 200),
        new_column("Stock UOM", "stock_uom", "Link", 90, options="UOM"),
        new_column("Variant Colour", "variant_color", "Data", 95),
        new_column("Voucher #", "voucher_no", "Data", 95),
        new_column("Project Code", "project_code", "Data", 95),
        new_column("Project Name", "project_name", "Link", 95, options="Project"),
        new_column("Qty", "actual_qty", "Float", 50),
        new_column("Balance Qty", "qty_after_transaction", "Float", 100),
    ]


def _get_project_code(project):
    return {project: frappe.db.get_value("Project", project, "ashbee_project_code")}


def _extract_projects(data):
    """
    Get projects from entries
    :param data:
    :return:
    """
    projects = compose(
        list,
        unique,
        partial(map, lambda x: x["project_name"]),  # extract project name
        partial(filter, lambda x: x["project_name"]),  # not empty
    )
    return projects(data)


def _get_stock_ledger_entries(filters):
    """
    Get data from Stock Ledger Entries with the following fields:
    (1) date, (2) item_code, (3) actual_qty, (4) qty_after_transaction,
    (5) project, (6) stock_uom, (7) item_name
    :param filters:
    :return: Stock Ledger Entries
    """
    item_code = filters.get("item_code")
    item_conditions = "AND sle.item_code = %(item_code)s" if item_code else ""

    return frappe.db.sql(
        """
        SELECT 
            CONCAT_WS(" ", sle.posting_date, sle.posting_time) AS date,
            sle.item_code, 
            sle.actual_qty, 
            sle.qty_after_transaction,
            sle.project AS project_name,
            sle.stock_uom,
            item.item_name,
            sle.voucher_no
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabItem` item ON sle.item_code = item.name
        WHERE sle.posting_date BETWEEN %(from_date)s AND %(to_date)s {item_conditions} {sle_conditions}
        ORDER BY 
            sle.posting_date ASC, 
            sle.posting_time ASC, 
            sle.creation ASC
        """.format(
            item_conditions=item_conditions, sle_conditions=get_sle_conditions(filters)
        ),
        filters,
        as_dict=1,
    )
