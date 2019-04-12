# Copyright (c) 2013, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _


# def printmsg(msglist):
# 	print("=="*8)
# 	print("\n"*8)
# 	for i in msglist:
# 		print(i)
# 	print("\n"*8)
# 	print("=="*8)

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_data(filters):
	fiscal_year = filters.get("fiscal_year")
	month = filters.get("month")
	overhead_percent = filters.get("overhead_percent")
	if None in [fiscal_year,month]:
		return []
	direct_expense_accounts = get_all_direct_expense_accounts()
	indirect_expense_accounts = get_all_indirect_expense_accounts()
	fiscal_year = frappe.get_doc("Fiscal Year", fiscal_year)
	journal_entries = get_all_journal_entries(fiscal_year, month)
	data = []
	projects = frappe.get_all("Project", fields="*")
	central_expense = get_central_expenses_sum(direct_expense_accounts, journal_entries, fiscal_year, month)
	indirect_expense = get_indirect_expenses_sum(indirect_expense_accounts,journal_entries, fiscal_year, month)
	
	for project in projects:
		should_append = False
		row = {}
		row['material_issue'] = get_material_issue_sum(project,fiscal_year,month)
		row['direct_cost'] = get_direct_cost_sum(journal_entries, project,fiscal_year,month)
		row['labour'] = get_labour_sum(project, fiscal_year, month)
		row['central_labour'] = get_central_labour_sum(project,fiscal_year, month)
		row['overhead_charges'] = get_overhead_charges_sum(row, overhead_percent)
		row['material_return'] = get_material_return_sum(project, fiscal_year, month)

		row['central_expenses'], central_expense = each_central_expense(row,central_expense)
		row['indirect_expenses'], indirect_expense = each_indirect_expense(row,indirect_expense)
		if all(i is None for i in row.values()):
			continue
		row['project'] = project.name
		data.append(row)


	return data

def each_central_expense(row, central_expense):
	'''Distribute Central Expenses for each project.'''
	costs = ['material_issue','labour','direct_cost']
	if all(row.get(i) is None for i in costs):
		return (None, central_expense)
	if central_expense <= 0:
		return (0, central_expense)
	cost = sum([row.get(i,0) or 0 for i in costs])
	if cost < central_expense:
		central_expense -= cost
		return (cost, central_expense)
	cost = central_expense
	central_expense = 0.0
	return (cost, central_expense)


def each_indirect_expense(row, indirect_expense):
	'''Distribute Indirect Expenses for each project.'''
	costs = ['material_issue','labour','direct_cost']
	if all(row.get(i) is None for i in costs):
		return (None, indirect_expense)
	if indirect_expense <= 0:
		return (0, indirect_expense)
	cost = sum([row.get(i,0) or 0 for i in costs])
	if cost < indirect_expense:
		indirect_expense -= cost
		return (cost, indirect_expense)
	cost = indirect_expense
	indirect_expense = 0.0
	return (cost, indirect_expense)


def get_material_issue_sum(project, fiscal_year, month):
	'''Sum of Total Outgoing Value on Materials Issued for related Project.'''
	amount = 0.0
	found = False
	filters = {"purpose":"Material Issue", "docstatus":1,"project":project.name}
	stock_entries = frappe.get_all("Stock Entry", filters=filters, fields="*")
	for stock_entry in stock_entries:
		if date_match_month(stock_entry.posting_date,fiscal_year,month):
			found = True
			amount += stock_entry.total_outgoing_value
	if found is False:
		return None
	return amount




def get_direct_cost_sum(journal_entries, project, fiscal_year, month):
	'''Sum of Debit amount on Journal Entry Accounts for related Project.'''
	amount = 0.0
	found = False
	filters = {'docstatus':1}
	for je in journal_entries:
		for je_account in je.accounts:
			if je_account.project != project.name:
				continue
			found = True
			amount += je_account.debit
	if found == False:
		return None
	return amount




def get_labour_sum(project, fiscal_year, month):
	'''Sum of Costing amount on Timesheet for related Project.'''
	amount = 0.0
	found = False
	filters = {"docstatus":1, "project":project.name}
	timesheet_details = frappe.get_all("Timesheet Detail", filters=filters, fields="*")
	for timesheet_detail in timesheet_details:
		if not date_match_month(timesheet_detail.to_time, fiscal_year, month):
			continue
		found = True
		amount += timesheet_detail.costing_amount
	if found == False:
		return None
	return amount

def get_central_labour_sum(project,fiscal_year, month):
	amount = 0.0
	found = False

	# TODO Pending confirmation
	return None

def get_central_expenses_sum(direct_expense_accounts, journal_entries, fiscal_year, month):
	'''Sum of Journal entry which is not against any project but have direct expense debit'''
	amount = 0.0
	found = False
	for je in journal_entries:
		for je_account in je.accounts:
			if je_account.account in direct_expense_accounts:
				found = True
				amount += je_account.debit
	if found == False:
		return None
	return amount

def get_indirect_expenses_sum(indirect_expense_accounts, journal_entries, fiscal_year, month):
	'''Sum of Journal entry which is not against any project but have indirect expense debit'''
	amount = 0.0
	found = False
	for je in journal_entries:
		for je_account in je.accounts:
			if je_account.account in indirect_expense_accounts:
				found = True
				amount += je_account.debit
	if found == False:
		return None
	return amount

def get_overhead_charges_sum(row, overhead_percent):
	'''Overhead Charges =(Material Issue + Labour + Direct Cost + Indirect expenses) / 20%'''
	if not overhead_percent:
		overhead_percent = 20.0
	if all(row.get(i) is None for i in ['material_issue','labour','indirect_expenses','direct_cost']):
		return None
	j = sum([row.get(i,0) or 0 for i in ['material_issue','labour','indirect_expenses','direct_cost']])
	return j * (flt(overhead_percent)/100)

def get_material_return_sum(project,fiscal_year, month):
	'''Sum of Total Incoming Value on Materials Returned for related Project.'''
	amount = 0.0
	found = False
	filters = {"purpose":"Material Receipt", "docstatus":1,"project":project.name}
	stock_entries = frappe.get_all("Stock Entry", filters=filters, fields="*")
	for stock_entry in stock_entries:
		if date_match_month(stock_entry.posting_date,fiscal_year,month):
			found = True
			amount += stock_entry.total_incoming_value
	if found is False:
		return None
	return amount


def get_all_journal_entries(fiscal_year, month):
	je_s = []
	filters = {'docstatus':1}
	journal_entries = frappe.get_all("Journal Entry", filters=filters, fields=["name","posting_date"])
	for je in journal_entries:
		if date_match_month(je.posting_date, fiscal_year, month):
			je = frappe.get_doc("Journal Entry", je.name)
			je_s.append(je)
	return je_s
		

def date_match_month(posting_date,fiscal_year, month):
	months = {'January':1,'February':2,'March':3,'April':4,'May':5,
				'June':6,'July':7,'August':8, 'September':9, 'October':10,
				'November':11,'December':12}
	if (int(posting_date.month) == int(months[month])) and (int(posting_date.year) == int(fiscal_year.year)):
		return True
	return False

def get_all_direct_expense_accounts():
	accounts = []
	filters = {'root_type':'Expense','is_group':False}
	_accounts = frappe.get_all("Account", filters=filters, fields="*")
	for account in _accounts:
		if is_direct_expense_account(account):
			accounts.append(account.name)
	return accounts

def get_all_indirect_expense_accounts():
	accounts = []
	filters = {'root_type':'Expense','is_group':False}
	_accounts = frappe.get_all("Account", filters=filters, fields="*")
	for account in _accounts:
		if is_indirect_expense_account(account):
			accounts.append(account.name)
	return accounts


def is_indirect_expense_account(account):
	if "indirect expenses" in account.parent_account.lower():
		return True
	account = frappe.get_doc("Account", account.parent_account)
	if account.is_group and account.parent_account:
		return is_indirect_expense_account(account)
	return False

def is_direct_expense_account(account):
	if "indirect expenses" not in account.parent_account.lower() and \
				"direct expenses" in account.parent_account.lower():
		return True
	account = frappe.get_doc("Account", account.parent_account)
	if account.is_group and account.parent_account:
		return is_direct_expense_account(account)
	return False


def get_columns(filters):
	return [
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options":"Project",
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
			"fieldtype": "Currency",
			"width": 120
		},
	]
