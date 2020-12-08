import frappe
from frappe import _


def salary_slip_save(doc, method):
    _set_ots(doc)
    _set_ot_salary_component(doc)


def _set_ots(doc):
    """
    Pre _set_ot_salary_component
    :param doc:
    :return:
    """
    def _get_ts_name(timesheet):
        return timesheet.get('time_sheet')

    timesheets = list(
        map(_get_ts_name, doc.timesheets)
    )

    timesheets_ots = frappe.get_all(
        'Timesheet',
        fields=['sum(ashbee_ot1) as ashbee_ot1', 'sum(ashbee_ot2) as ashbee_ot2'],
        filters=[['name', 'in', timesheets], ['docstatus', '=', '1']]
    )[0]

    doc.ashbee_ot1 = timesheets_ots.get('ashbee_ot1', 0) or 0
    doc.ashbee_ot2 = timesheets_ots.get('ashbee_ot2', 0) or 0


def _set_ot_salary_component(doc):
    overtime = frappe.db.get_single_value('Ashbee Settings', 'overtime')

    if not overtime:
        frappe.throw(_('Set Overtime salary component under Ashbee Settings'))

    salary_components = map(lambda x: x.salary_component, doc.earnings)

    if overtime in salary_components:
        return

    ot1_rate = 1.25
    ot2_rate = 1.50

    ot1_amount = doc.ashbee_ot1 * (doc.hour_rate * ot1_rate)
    ot2_amount = doc.ashbee_ot2 * (doc.hour_rate * ot2_rate)

    doc.append('earnings', {
        'salary_component': overtime,
        'amount': ot1_amount + ot2_amount
    })

    # Update the net pay from here
    doc.calculate_net_pay()
