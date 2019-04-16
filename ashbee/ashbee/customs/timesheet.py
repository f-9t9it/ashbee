import frappe
from frappe.utils import flt


def timesheet_save(doc, d):
	pass
	# for detail in doc.time_logs:
	# 	if not detail.billable:
	# 		continue
	# 	detail.ashbee_ot = flt(detail.ashbee_ot) or 0.0
	# 	detail.ashbee_ot2 = flt(detail.ashbee_ot2) or 0.0
	# 	detail.costing_amount = flt(detail.costing_amount) or 0.0
	# 	doc.total_costing_amount = flt(doc.total_costing_amount) or 0.0

	# 	detail.costing_amount += detail.ashbee_ot + detail.ashbee_ot2
	# 	doc.total_costing_amount += detail.ashbee_ot + detail.ashbee_ot2
	# 	