import frappe
from ashbee.api import get_latest_valuation_rate


def item_save(doc, d):
	if doc.variant_of:
		ashbee_bar = frappe.db.get_value('Item', doc.variant_of, 'ashbee_bar')
		doc.ashbee_bar = ashbee_bar
	if doc.ashbee_bar:
		doc.weight_per_unit = doc.ashbee_weight
	_validate_valuation_rate(doc)


def _validate_valuation_rate(item):
	if item.variant_of:
		template_valuation_rate = frappe.get_value('Item', item.variant_of, 'valuation_rate')
		if not template_valuation_rate:
			item.valuation_rate = get_latest_valuation_rate(item.variant_of)
