# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today
from erpnext.hr.doctype.salary_structure_assignment.salary_structure_assignment import get_assigned_salary_structure


class BulkTimesheetEntry(Document):
    def validate(self):
        self.validate_costs()

    def on_submit(self):
        self.update_timesheet()

    def on_cancel(self):
        self.bulk_cancel()

    def get_employee_details(self, employee):
        employee = frappe.get_doc("Employee", employee)
        return {
            "name": employee.employee_name,
            "rate": self.get_employee_charge_per_hour(employee)
        }

    def get_project_name(self, project):
        project = frappe.get_doc("Project", project)
        return project.name

    def get_employee_charge_per_hour(self, employee):
        salary_structure = get_assigned_salary_structure(employee.name, today())
        if not salary_structure:
            return 0.0
        salary_structure = frappe.get_doc("Salary Structure", salary_structure)
        if salary_structure.docstatus != 1 or not salary_structure.is_active == "Yes" or \
                not salary_structure.salary_slip_based_on_timesheet:
            return 0.0
        return salary_structure.hour_rate

    def validate_costs(self):
        for detail in self.details:
            detail.normal_cost = detail.hourly_cost * detail.normal_hours
            detail.ot1 = detail.hourly_cost * detail.ot1_hours
            detail.ot2 = detail.hourly_cost * detail.ot2_hours
            detail.total_cost = detail.ot1 + detail.ot2 + detail.normal_cost

    def bulk_cancel(self):
        for detail in self.details:
            if detail.timesheet:
                timesheet = frappe.get_doc("Timesheet", detail.timesheet)
                timesheet.cancel()

    def bulk_delete(self):
        to_delete = []
        filters = {"parent": self.name}
        fields = ["name", "timesheet"]

        timesheet_details = frappe.get_all("Bulk Timesheet Details", filters=filters, fields=fields)

        for detail in timesheet_details:
            if not self.details or detail.name not in [i.name for i in self.details]:
                to_delete.append(detail.timesheet)
        for d in to_delete:
            self.delete_timesheet(d)

    def delete_timesheet(self, timesheet):
        if not timesheet:
            return
        if isinstance(timesheet, str) or isinstance(timesheet, unicode):
            timesheet = frappe.get_doc("Timesheet", timesheet)
        timesheet.cancel()
        timesheet.delete()

    def update_timesheet(self):
        for detail in self.details:
            self.delete_timesheet(detail.timesheet)
            timesheet = _create_timesheet(self.company, detail)
            _set_detail_timesheet(detail.name, timesheet.name)

        frappe.db.commit()


def _create_timesheet(company, detail):
    timesheet = frappe.new_doc('Timesheet')
    timesheet.company = company
    timesheet.employee = detail.employee
    timesheet.time_logs = _get_timesheet_timelogs(timesheet, detail)
    timesheet.ashbee_ot1 = detail.ot1_hours
    timesheet.ashbee_ot2 = detail.ot2_hours
    timesheet.save(ignore_permissions=True)
    timesheet.submit()

    return timesheet


def _set_detail_timesheet(name, timesheet):
    frappe.db.set_value('Bulk Timesheet Details', name, 'timesheet', timesheet)


def _get_timesheet_timelogs(timesheet, entry_detail):
    timesheet_details = []

    if not hasattr(timesheet, "time_logs") or not timesheet.time_logs:
        detail = frappe.new_doc("Timesheet Detail")
    else:
        detail = timesheet.time_logs[0]

    detail.parentfield = "time_logs"
    detail.activity_type = entry_detail.activity_type
    detail.hours = entry_detail.normal_hours
    detail.from_time = entry_detail.start_date_time
    detail.to_time = entry_detail.end_date_time
    detail.billable = True
    detail.costing_rate = entry_detail.hourly_cost
    detail.costing_amount = entry_detail.total_cost
    detail.project = entry_detail.project
    detail.ashbee_ot = entry_detail.ot1
    detail.ashbee_ot2 = entry_detail.ot2
    timesheet_details.append(detail)

    return timesheet_details