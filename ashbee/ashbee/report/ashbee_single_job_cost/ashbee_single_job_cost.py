# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from toolz import merge, partial, compose
import frappe
import pprint

from ashbee.helpers import new_column, fill_item_name, total_to_column, exclude_items, fill_timesheet_month, sort_timesheet
from ashbee.utils.project import get_labour_expenses, get_consumed_material_cost, get_purchase_cost, \
    get_central_allocations, get_indirect_costs, get_direct_costs


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)

    # header = _get_header(filters)

    if data:
        total_row = _get_total_row(data, '<b>Grand Total</b>')
        overhead_charges = _fill_overhead_charges(total_row, filters.get('overhead_percent') / 100.00)
        total_row['overhead_charges'] = overhead_charges
        data.append(total_row)
        data = list(
            map(_compute_row_wise_total, data)
        )

    return columns, data


def get_columns():
    return [
        new_column("Reference", "reference", "Data", 180),
        new_column("Date", "date", "Date", 95),
        new_column("Description", "description", "Data", 200),
        new_column("Income", "income", "Currency", 90),
        new_column("Qty", "qty", "Int", 90),
        new_column("Rate", "rate", "Currency", 90),
        new_column("Material+Direct", "material_direct", "Currency", 120),
        new_column("Labor Expenses", "labor_expenses", "Currency", 120),
        new_column("Central Labour", "central_labour", "Currency", 120),
        new_column("Central Expenses", "central_expenses", "Currency", 120),
        new_column("Indirect", "indirect", "Currency", 120),
        new_column("Overhead Charges", "overhead_charges", "Currency", 120),
        new_column("Total", "total", "Currency", 120)
    ]


def get_data(filters):
    data = []
    # overhead_percent = filters.get('overhead_percent') / 100.00

    # project_expenses = _get_project_expenses(filters)
    # project_expenses['overhead_charges'] = _fill_overhead_charges(
    #     project_expenses,
    #     overhead_percent
    # )
    #
    # data.append(project_expenses)

    entries = [
        _get_stock_ledger_entries(filters),
        _get_purchase_cost_items(filters),
        _get_central_labor_items(filters),
        _get_central_expense_items(filters),
        _get_indirect_cost_items(filters),
    ]

    for entry in entries:
        data.extend(entry)

    data.sort(
        key=lambda x: x['date'],
        reverse=filters.get('date_ascending', False)
    )

    # Direct Cost
    data.extend(_get_direct_cost_items(filters))

    # Separated as timesheet has no date for sort
    data.extend(_get_timesheet_details(filters))

    return data


def _get_project_expenses(filters):
    labour_expenses = get_labour_expenses(filters)
    filtered_sum = compose(sum, partial(filter, lambda x: x))
    material_direct = {
        'material_direct': filtered_sum(
            merge(
                get_consumed_material_cost(filters),
                get_purchase_cost(filters)
            ).values()
        )
    }

    central_allocations = get_central_allocations(filters)
    indirect = get_indirect_costs(filters)

    return merge(
        labour_expenses,
        material_direct,
        central_allocations,
        indirect
    )


@fill_item_name
@total_to_column(column='material_direct')
@exclude_items(items=['Othr-000-0'])
def _get_stock_ledger_entries(filters):
    return frappe.db.sql("""
        SELECT 
            posting_date AS date, 
            voucher_no AS reference, 
            item_code AS description,
            valuation_rate AS rate,
            actual_qty AS qty
        FROM `tabStock Ledger Entry`
        WHERE project=%(project)s 
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)


@sort_timesheet
@fill_timesheet_month
def _get_timesheet_details(filters):
    return frappe.db.sql("""
        SELECT 
            'Timesheet' AS description,
            MONTHNAME(start_date) AS timesheet_month,
            COALESCE(SUM(costing_amount), 0) AS labor_expenses, 
            COALESCE(COUNT(*), 0) AS qty,
            start_date
        FROM `tabTimesheet Detail`
        INNER JOIN `tabTimesheet`
        ON `tabTimesheet Detail`.parent = `tabTimesheet`.name
        WHERE `tabTimesheet Detail`.project=%(project)s
        AND `tabTimesheet Detail`.docstatus=1
        AND start_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY MONTH(start_date)
    """, filters, as_dict=1)


def _get_total_row(data, description='Total'):
    columns_for_total = _get_columns_for_total()
    total_row = {column: 0.00 for column in columns_for_total}

    for column in total_row.keys():
        total_row[column] = sum([abs(row.get(column, 0.00)) for row in data])

    total_row['description'] = description

    return total_row

    # total_qty = 0
    # total_rate = 0.00
    # for row in data:
    #     total_qty = total_qty + (row.get('qty') or 0)
    #     total_rate = total_rate + (row.get('rate') or 0)
    # return {
    #     'description': description,
    #     'qty': total_qty,
    #     'rate': total_rate
    # }


def _fill_overhead_charges(project_expenses, overhead_percent):
    material_direct = project_expenses.get('material_direct', 0.00)
    labor_expenses = project_expenses.get('labor_expenses', 0.00)
    indirect = project_expenses.get('indirect', 0.00)

    return (material_direct + labor_expenses + indirect) * overhead_percent


def _fill_blank(data):
    data.append({})


def _get_header(filters):
    project = filters.get('project')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    project_code = _get_project_code(project)

    return [
        {'reference': '<b>ASHBEE METAL CLADDING WILL</b>'},
        {'reference': '<i>Job Income Expense Report</i>'},
        {},
        {'reference': '{} - {}'.format(project_code, project)},
        {'reference': '<i>From {} To {}</i>'.format(from_date, to_date)},
        {}
    ]


def _get_project_code(project):
    return frappe.db.get_value('Project', project, 'ashbee_project_code')


@total_to_column(column='material_direct')
def _get_purchase_cost_items(filters):
    return frappe.db.sql("""
        SELECT
            doc.posting_date AS date,
            doc.name AS reference,
            'Purchase Invoice' AS description,
            item.rate,
            item.qty
        FROM `tabPurchase Invoice Item` item
        INNER JOIN `tabPurchase Invoice` doc
        ON item.parent = doc.name
        WHERE doc.docstatus = 1
        AND project = %(project)s
        AND posting_date
        BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)


@total_to_column(column='central_labour')
def _get_central_labor_items(filters):
    return frappe.db.sql("""
        SELECT
            ce.posting_date AS date,
            ce.name AS reference,
            'Direct Labour' AS description,
            cep.labor_allocation AS rate,
            1 AS qty           
        FROM `tabCentral Expense Project` cep
        INNER JOIN `tabCentral Expense` ce
        ON cep.parent = ce.name
        WHERE ce.docstatus = 1
        AND project = %(project)s
        AND from_date <= %(to_date)s
        AND to_date >= %(from_date)s
    """, filters, as_dict=1)


@total_to_column(column='central_expenses')
def _get_central_expense_items(filters):
    return frappe.db.sql("""
        SELECT
            ce.posting_date AS date,
            ce.name AS reference,
            'Direct Cost Allocation' AS description,
            cep.allocation AS rate,
            1 AS qty           
        FROM `tabCentral Expense Project` cep
        INNER JOIN `tabCentral Expense` ce
        ON cep.parent = ce.name
        WHERE ce.docstatus = 1
        AND project = %(project)s
        AND from_date <= %(to_date)s
        AND to_date >= %(from_date)s
    """, filters, as_dict=1)


@total_to_column(column='indirect')
def _get_indirect_cost_items(filters):
    return frappe.db.sql("""
        SELECT 
            doc.posting_date AS date,
            doc.name AS reference,
            'Indirect Cost Allocation' AS description,
            item.allocated AS rate,
            1 AS qty
        FROM `tabIndirect Cost Item` item
        INNER JOIN `tabIndirect Cost` doc
        ON item.parent = doc.name
        WHERE doc.docstatus = 1
        AND project = %(project)s
        AND start_date <= %(to_date)s
        AND end_date >= %(from_date)s
    """, filters, as_dict=1)


def _get_direct_cost_items(filters):
    return frappe.db.sql("""
        SELECT 
            item.posting_date AS date,
            `tabDirect Cost`.name AS reference,
            item.direct_cost AS material_direct,
            item.narration AS description,
            1 AS qty
        FROM `tabDirect Cost Item` item
        INNER JOIN `tabDirect Cost`
        ON item.parent = `tabDirect Cost`.name
        WHERE `tabDirect Cost`.docstatus = 1
        AND job_no = %(project)s
        AND item.posting_date
        BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)


def _get_columns_for_total():
    return [
        'qty',
        'rate',
        'material_direct',
        'labor_expenses',
        'central_labour',
        'central_expenses',
        'indirect',
        'overhead_charges'
    ]


def _compute_row_wise_total(row):
    columns = [
        'rate',
        'material_direct',
        'labor_expenses',
        'central_labour',
        'central_expenses',
        'indirect',
        'overhead_charges'
    ]

    values = [row.get(column, 0.00) for column in columns]

    row['total'] = sum(values)

    return row
