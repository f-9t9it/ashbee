# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ashbee.utils import get_costs_by_projects

from toolz import partial, reduce


class CentralExpense(Document):
    def validate(self):
        self.items = []
        self.projects = []

        # date_range = get_month_date_range(self.posting_date)
        filters = {'from_date': self.from_date, 'to_date': self.to_date, 'company': self.company}

        central_entries = _get_central_entries(filters)
        self._set_central_entries(central_entries)

        projects = get_costs_by_projects(filters)
        self._set_projects(projects)

    def on_submit(self):
        _set_project_costing(self.projects)

    def on_cancel(self):
        _set_project_costing(self.projects, True)

    def _set_central_entries(self, central_entries):
        append_and_sum = partial(_append_and_sum_central_entry, self)
        allocation = reduce(append_and_sum, central_entries, {
            'labor_allocation': 0.00,
            'cost_allocation': 0.00
        })
        self.labor_allocation = allocation['labor_allocation']
        self.cost_allocation = allocation['cost_allocation']
        self.total_allocation = self.labor_allocation + self.cost_allocation

    def _set_projects(self, projects):
        total_cost = reduce(lambda x, y: x + y, projects.values(), 0)
        for project, cost in projects.items():
            ratio = cost / total_cost
            allocation = self.cost_allocation * ratio
            labor_allocation = self.labor_allocation * ratio
            self.append('projects', {
                'project': project,
                'cost': cost,
                'ratio': ratio,
                'allocation': allocation,
                'labor_allocation': labor_allocation
            })
        self.total_cost = total_cost


def _get_central_entries(filters):
    return frappe.db.sql("""
		SELECT name AS central_entry, voucher_type AS entry_type, allocation
		FROM `tabCentral Entry`
		WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
		AND docstatus = 1
        AND company = %(company)s
	""", filters, as_dict=1)


def _append_and_sum_central_entry(central_expense, x, y):
    """
    Use central expense to append to the table,
    and summation of x and y (used for reduce)
    :param central_expense:
    :param x: allocation; labor and cost
    :param y: Central Entry
    :return: allocation
    """
    central_expense.append('items', y)

    allocation = y['allocation']
    entry_type = y['entry_type']

    costs_type = ['Stock Entry', 'Direct Cost', 'Purchase Invoice']

    if entry_type in costs_type:
        cost_allocation = x['cost_allocation'] + allocation
        x['cost_allocation'] = cost_allocation
    elif entry_type == 'Timesheet':
        labor_allocation = x['labor_allocation'] + allocation
        x['labor_allocation'] = labor_allocation

    return x


def _set_project_costing(items, cancel=False):
    for item in items:
        central_labor = _get_project_central_value(item.project, 'Timesheet')
        central_cost = _get_project_central_value(item.project, 'Stock Entry')

        allocation = item.allocation if not cancel else -item.allocation
        labor_allocation = item.labor_allocation if not cancel else -item.labor_allocation

        _set_project_central_value(item.project, 'Timesheet', central_labor + labor_allocation)
        _set_project_central_value(item.project, 'Stock Entry', central_cost + allocation)

    frappe.db.commit()


def _get_project_central_value(project, entry_type):
    fields = {
        'Timesheet': 'ashbee_total_central_labor',
        'Stock Entry': 'ashbee_total_central_cost'
    }

    return frappe.db.get_value('Project', project, fields[entry_type])


def _set_project_central_value(project, entry_type, value):
    fields = {
        'Timesheet': 'ashbee_total_central_labor',
        'Stock Entry': 'ashbee_total_central_cost'
    }

    frappe.db.set_value('Project', project, fields[entry_type], value)
