import frappe


def item_save(doc, d):
	if doc.variant_of:
		ashbee_bar = frappe.db.get_value('Item', doc.variant_of, 'ashbee_bar')
		doc.ashbee_bar = ashbee_bar
	if doc.ashbee_bar:
		doc.weight_per_unit = doc.ashbee_weight