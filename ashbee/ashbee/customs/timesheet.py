import frappe
from frappe.utils import flt
from ashbee.utils import get_central_entry


def timesheet_save(doc, d):
    for detail in doc.time_logs:
        if not detail.billable:
            continue
        detail.ashbee_ot = flt(detail.ashbee_ot) or 0.0
        detail.ashbee_ot2 = flt(detail.ashbee_ot2) or 0.0
        detail.costing_amount = flt(detail.costing_amount) or 0.0
        doc.total_costing_amount = flt(doc.total_costing_amount) or 0.0

        detail.costing_amount += detail.ashbee_ot + detail.ashbee_ot2
        doc.total_costing_amount += detail.ashbee_ot + detail.ashbee_ot2


def timesheet_submit(doc, d):
    central_project = frappe.db.get_single_value('Ashbee Settings', 'central_project')

    for detail in doc.time_logs:
        if detail.project == central_project:
            central_entry = _create_central_entry(doc, detail)
            central_entry.submit()


def timesheet_cancel(doc, d):
    _cancel_central_entry(doc)


def _cancel_central_entry(doc):
    for detail in doc.time_logs:
        central_entry = get_central_entry(doc.name, detail.name)
        if central_entry:
            central_entry.cancel()


def _create_central_entry(doc, detail):
    return frappe.get_doc({
        'doctype': 'Central Entry',
        'posting_date': doc.start_date,
        'voucher_type': 'Timesheet',
        'voucher_no': doc.name,
        'voucher_detail_no': detail.name,
        'allocation': detail.costing_amount
    }).insert()
