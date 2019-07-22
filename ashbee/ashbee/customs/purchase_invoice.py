import frappe
from ashbee.utils import check_central_expense


def purchase_invoice_save(doc, method):
    check_central_expense(doc.posting_date)


def purchase_invoice_submit(doc, method):
    _set_central_entry(doc)


def purchase_invoice_cancel(doc, method):
    _cancel_central_entry(doc)


def _set_central_entry(doc):
    for item in doc.items:
        _create_central_entry(doc, item)


def _cancel_central_entry(doc):
    for item in doc.items:
        if item.ashbee_central_entry:
            central_entry = frappe.get_doc(
                'Central Entry',
                item.ashbee_central_entry
            )

            central_entry.cancel()


def _create_central_entry(doc, item):
    central_entry = frappe.db.get_single_value('Ashbee Settings', 'central_project')

    if item.project != central_entry:
        return

    central_entry = frappe.get_doc({
        'doctype': 'Central Entry',
        'posting_date': doc.posting_date,
        'voucher_type': 'Purchase Invoice',
        'voucher_no': doc.name,
        'voucher_detail_no': item.name,
        'allocation': item.amount
    }).insert()

    central_entry.submit()

    frappe.db.set_value(
        'Purchase Invoice Item',
        item.name,
        'ashbee_central_entry',
        central_entry.name
    )
