# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import itertools
from frappe import _
from ashbee.utils import get_all_timesheet_details, get_all_direct_costs, get_all_material_issues,\
    get_all_indirect_costs, get_central_expenses, get_central_labour, get_all_material_returns


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    return [
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
            "label": _("Central Labour"),
            "fieldname": "central_labour",
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

    for project, costs in costs_by_projects:
        project_data = {}

        for cost in costs:
            project_data.update(cost)

        if project is None:
            project_data.update({'project': 'Other Projects'})

        res_data.append(project_data)

    # Transform fieldnames to right report fields
    _rename_fieldnames_for_report(res_data)

    # Charges and Sum
    _fill_overhead_charges(res_data, filters.get('overhead_percent'))
    _sum_costs(res_data)

    # Add central formula
    central_labour = get_central_labour(filters)
    central_expenses = get_central_expenses(filters)
    total_sum_costs = _sum_costs(res_data)

    _fill_central_fields(
        res_data,
        central_labour,
        central_expenses,
        total_sum_costs
    )

    return res_data


def _fill_central_fields(data, labour, expenses, sum_costs):
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

# def each_central_expense(row, central_expense):
# 	'''Distribute Central Expenses for each project.'''
# 	costs = ['material_issue','labour','direct_cost']
# 	if all(row.get(i) is None for i in costs):
# 		return (None, central_expense)
# 	if central_expense <= 0:
# 		return (0, central_expense)
# 	cost = sum([row.get(i,0) or 0 for i in costs])
# 	if cost < central_expense:
# 		central_expense -= cost
# 		return (cost, central_expense)
# 	cost = central_expense
# 	central_expense = 0.0
# 	return (cost, central_expense)
#
#
# def each_indirect_expense(row, indirect_expense):
# 	'''Distribute Indirect Expenses for each project.'''
# 	costs = ['material_issue','labour','direct_cost']
# 	if all(row.get(i) is None for i in costs):
# 		return (None, indirect_expense)
# 	if indirect_expense <= 0:
# 		return (0, indirect_expense)
# 	cost = sum([row.get(i,0) or 0 for i in costs])
# 	if cost < indirect_expense:
# 		indirect_expense -= cost
# 		return (cost, indirect_expense)
# 	cost = indirect_expense
# 	indirect_expense = 0.0
# 	return (cost, indirect_expense)
#
#
# def get_material_issue_sum(project, timespan):
# 	'''Sum of Total Outgoing Value on Materials Issued for related Project.'''
# 	amount = 0.0
# 	found = False
# 	filters = {"purpose":"Material Issue", "docstatus":1,"project":project.name}
# 	stock_entries = frappe.get_all("Stock Entry", filters=filters, fields="*")
# 	for stock_entry in stock_entries:
# 		if date_match_month(stock_entry.posting_date,timespan):
# 			found = True
# 			amount += stock_entry.total_outgoing_value
# 	if found is False:
# 		return None
# 	return amount
#
#
# def get_direct_cost_sum(journal_entries, project, timespan):
# 	'''Sum of Debit amount on Journal Entry Accounts for related Project.'''
# 	amount = 0.0
# 	found = False
# 	filters = {'docstatus':1}
# 	for je in journal_entries:
# 		for je_account in je.accounts:
# 			if je_account.project != project.name:
# 				continue
# 			found = True
# 			amount += je_account.debit
# 	if found == False:
# 		return None
# 	return amount
#
#
# def get_labour_sum(project,timespan):
# 	'''Sum of Costing amount on Timesheet for related Project.'''
# 	amount = 0.0
# 	found = False
# 	filters = {"docstatus":1, "project":project.name}
# 	timesheet_details = frappe.get_all("Timesheet Detail", filters=filters, fields="*")
# 	for timesheet_detail in timesheet_details:
# 		if not date_match_month(timesheet_detail.to_time, timespan):
# 			continue
# 		found = True
# 		amount += timesheet_detail.costing_amount
# 	if found == False:
# 		return None
# 	return amount
#
#
# def get_central_labour_sum(project,timespan):
# 	'''Sum of Costing amount on Timesheet for related Project.'''
# 	amount = 0.0
# 	found = False
# 	filters = {"docstatus":1, "project":project.name}
# 	timesheet_details = frappe.get_all("Timesheet Detail", filters=filters, fields="*")
# 	for timesheet_detail in timesheet_details:
# 		if not date_match_month(timesheet_detail.to_time, timespan):
# 			continue
# 		found = True
# 		amount += timesheet_detail.costing_amount
# 	if found == False:
# 		return None
# 	return amount
#
#
# def get_central_expenses_sum(direct_expense_accounts, journal_entries, timespan):
# 	'''Sum of Journal entry which is not against any project but have direct expense debit'''
# 	amount = 0.0
# 	found = False
# 	for je in journal_entries:
# 		for je_account in je.accounts:
# 			if je_account.account in direct_expense_accounts:
# 				found = True
# 				amount += je_account.debit
# 	if found == False:
# 		return None
# 	return amount
#
#
# def get_indirect_expenses_sum(indirect_expense_accounts, journal_entries, timespan):
# 	'''Sum of Journal entry which is not against any project but have indirect expense debit'''
# 	amount = 0.0
# 	found = False
# 	for je in journal_entries:
# 		for je_account in je.accounts:
# 			if je_account.account in indirect_expense_accounts:
# 				found = True
# 				amount += je_account.debit
# 	if found == False:
# 		return None
# 	return amount
#
#
# def get_overhead_charges_sum(row, overhead_percent):
# 	'''Overhead Charges =(Material Issue + Labour + Direct Cost + Indirect expenses) / 20%'''
# 	if not overhead_percent:
# 		overhead_percent = 20.0
# 	if all(row.get(i) is None for i in ['material_issue','labour','indirect_expenses','direct_cost']):
# 		return None
# 	j = sum([row.get(i,0) or 0 for i in ['material_issue','labour','indirect_expenses','direct_cost']])
# 	return j * (flt(overhead_percent)/100)
#
#
# def get_material_return_sum(project,timespan):
# 	'''Sum of Total Incoming Value on Materials Returned for related Project.'''
# 	amount = 0.0
# 	found = False
# 	filters = {"purpose":"Material Receipt", "docstatus":1,"project":project.name}
# 	stock_entries = frappe.get_all("Stock Entry", filters=filters, fields="*")
# 	for stock_entry in stock_entries:
# 		if date_match_month(stock_entry.posting_date,timespan):
# 			found = True
# 			amount += stock_entry.total_incoming_value
# 	if found is False:
# 		return None
# 	return amount
#
#
# def get_all_journal_entries(timespan):
# 	je_s = []
# 	filters = {'docstatus':1}
# 	journal_entries = frappe.get_all("Journal Entry", filters=filters, fields=["name","posting_date"])
# 	for je in journal_entries:
# 		if date_match_month(je.posting_date, timespan):
# 			je = frappe.get_doc("Journal Entry", je.name)
# 			je_s.append(je)
# 	return je_s
#
#
# def date_match_month(posting_date,timespan):
# 	from_date, to_date = timespan
# 	if isinstance(posting_date, datetime):
# 		posting_date = posting_date.date()
# 	if posting_date > getdate(from_date) and posting_date < getdate(to_date):
# 		return True
# 	return False
#
#
# def get_all_direct_expense_accounts():
# 	accounts = []
# 	filters = {'root_type':'Expense','is_group':False}
# 	_accounts = frappe.get_all("Account", filters=filters, fields="*")
# 	for account in _accounts:
# 		if is_direct_expense_account(account):
# 			accounts.append(account.name)
# 	return accounts
#
#
# def get_all_indirect_expense_accounts():
# 	accounts = []
# 	filters = {'root_type':'Expense','is_group':False}
# 	_accounts = frappe.get_all("Account", filters=filters, fields="*")
# 	for account in _accounts:
# 		if is_indirect_expense_account(account):
# 			accounts.append(account.name)
# 	return accounts
#
#
# def is_indirect_expense_account(account):
# 	if "indirect expenses" in account.parent_account.lower():
# 		return True
# 	account = frappe.get_doc("Account", account.parent_account)
# 	if account.is_group and account.parent_account:
# 		return is_indirect_expense_account(account)
# 	return False
#
#
# def is_direct_expense_account(account):
# 	if "indirect expenses" not in account.parent_account.lower() and \
# 				"direct expenses" in account.parent_account.lower():
# 		return True
# 	account = frappe.get_doc("Account", account.parent_account)
# 	if account.is_group and account.parent_account:
# 		return is_direct_expense_account(account)
# 	return False
