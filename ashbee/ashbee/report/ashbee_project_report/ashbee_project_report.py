# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import itertools
import frappe
from frappe import _
from frappe.utils.data import formatdate, now_datetime
from ashbee.helpers import round_off_rows
from ashbee.utils import get_all_timesheet_details, get_all_direct_costs, get_all_material_issues,\
    get_all_indirect_costs, get_all_material_returns, get_central_costs, get_excluded_projects


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)

    if data:
        _fill_rows_total(data)
        _fill_totals(data)

        round_off_rows(data, [
            'material_issue',
            'direct_cost',
            'labour',
            'central_labour',
            'central_expenses',
            'indirect_expenses',
            'overhead_charges',
            'total'
        ])

        data.extend(
            _get_print_details_row(filters)
        )

        _fill_rows_project_code(data)

    return columns, data


def get_columns(filters):
    return [
        {
            "label": _("Project Code"),
            "fieldname": "project_code",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        },
        {
            "label": _("Material Issue"),
            "fieldname": "material_issue",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Direct Cost"),
            "fieldname": "direct_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Labour"),
            "fieldname": "labour",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Central Expenses"),
            "fieldname": "central_expenses",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Central Labour"),
            "fieldname": "central_labour",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Indirect Expenses"),
            "fieldname": "indirect_expenses",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Overhead Charges"),
            "fieldname": "overhead_charges",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Material Return"),
            "fieldname": "material_return",
            "fieldtype": "Integer",
            "width": 60
        },
        {
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters):
    res_data = []

    # Get all costs
    data = sum([
        get_all_material_issues(filters),
        get_all_indirect_costs(filters),
        get_all_direct_costs(filters),
        get_all_timesheet_details(filters),
        get_all_material_returns(filters)
    ], [])

    # Group by projects
    def keyfunc(x):
        return x['project']

    data = sorted(data, key=keyfunc)
    costs_by_projects = itertools.groupby(data, key=keyfunc)
    excluded_projects = get_excluded_projects()

    for project, costs in costs_by_projects:
        if project in excluded_projects or project == '':
            continue

        project_data = {}

        for cost in costs:
            project_data.update(cost)

        res_data.append(project_data)

    # Transform fieldnames to right report fields
    _rename_fieldnames_for_report(res_data)

    # Charges and Sum
    _fill_overhead_charges(res_data, filters.get('overhead_percent'))
    _sum_costs(res_data)

    # Add central formula
    # central_labour = get_central_labour(filters)
    # central_expenses = get_central_expenses(filters)
    # total_sum_costs = _sum_costs(res_data)

    central_costs = _group_centrals(
        get_central_costs(filters)
    )

    _fill_central_costs(res_data, central_costs)

    # _fill_central_fields(
    #     res_data,
    #     central_labour,
    #     central_expenses,
    #     total_sum_costs
    # )

    return res_data


def _get_print_details_row(filters):
    from_date = formatdate(filters.get('from_date'), 'dd-mm-yyyy')
    to_date = formatdate(filters.get('to_date'), 'dd-mm-yyyy')
    printed_on = now_datetime().strftime('%d-%m-%Y %H:%M:%S')

    return [
        {},
        {'project': 'From Date: {}'.format(from_date)},
        {'project': 'To Date: {}'.format(to_date)},
        {'project': 'Printed On: {}'.format(printed_on)}
    ]


def _group_centrals(data):
    centrals = {}

    for row in data:
        project = row.get('project')
        cost = row.get('allocation')
        labor = row.get('labor_allocation')

        if not(project in centrals):
            centrals[project] = {'cost': cost, 'labor': labor}
        else:
            total_cost = centrals[project].get('cost') + cost
            total_labor = centrals[project].get('labor') + total_labor
            centrals[project]['cost'] = total_cost
            centrals[project]['labor'] = total_labor

    return centrals


def _fill_central_costs(data, central_costs):
    for row in data:
        project = row.get('project')

        row['central_labour'] = 0.00
        row['central_expenses'] = 0.00

        if central_costs.get(project, None):
            row['central_labour'] = central_costs[project].get('labor')
            row['central_expenses'] = central_costs[project].get('cost')


def _fill_central_fields(data, labour, expenses, sum_costs):
    # TODO: deprecated
    if not labour:
        labour = 0.00
    if not expenses:
        expenses = 0.00
    for row in data:
        row['central_labour'] = labour * (row['dividend'] / sum_costs)
        row['central_expenses'] = expenses * (row['dividend'] / sum_costs)


def _sum_costs(data):
    total_sum_costs = 0.0
    for row in data:
        row['dividend'] = sum([
            row['material_issue'],
            row['direct_cost'],
            row['labour']
        ])
        total_sum_costs = total_sum_costs + row['dividend']
    return total_sum_costs


def _fill_overhead_charges(data, overhead):
    for row in data:
        row['overhead_charges'] = sum([
            row['material_issue'],
            row['direct_cost'],
            row['labour'],
            row['indirect_expenses']
        ]) * (overhead / 100.00)


def _rename_fieldnames_for_report(data):
    fieldnames = {
        'sum_total_outgoing_value': 'material_issue',
        'sum_direct_cost': 'direct_cost',
        'sum_costing_amount': 'labour',
        'sum_allocated': 'indirect_expenses'
    }

    for row in data:
        for current, new in fieldnames.iteritems():
            if current in row:
                row[new] = row.pop(current)
            else:
                row[new] = 0.00


def _fill_totals(data):
    total_row = {
        'material_issue': 0.000,
        'direct_cost': 0.000,
        'labour': 0.000,
        'central_labour': 0.000,
        'central_expenses': 0.000,
        'indirect_expenses': 0.000,
        'overhead_charges': 0.000,
        'material_return': 0,
        'total': 0.00
    }

    for row in data:
        for key, value in total_row.items():
            row_value = row.get(key) or 0.00
            total_row[key] = value + row_value

    total_row['project'] = 'Total:'

    data.append(total_row)


def _fill_rows_total(data):
    compute_fields = [
        'material_issue',
        'direct_cost',
        'labour',
        'central_labour',
        'central_expenses',
        'indirect_expenses',
        'overhead_charges'
    ]

    for row in data:
        row['total'] = sum([row.get(field) for field in compute_fields])


def _fill_rows_project_code(data):
    filters = {'is_active': 'Yes'}
    fields = ['name', 'ashbee_project_code']

    projects = frappe.get_all('Project', filters=filters, fields=fields)
    project_codes = {project.get('name'): project.get('ashbee_project_code') for project in projects}

    for row in data:
        project = row.get('project')
        if project_codes.get(project, None):
            row['project_code'] = project_codes[project]
