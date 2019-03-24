import frappe


@frappe.whitelist()
def get_variant_items(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	if not filters.get("item_code") or not filters.get("attr_type"):
		return []
	item = frappe.get_doc("Item", filters.get("item_code"))
	if not item.variant_of:
		return []
	attr_type = filters.get("attr_type")
	return frappe.db.sql('''select name from tabItem where name != "{item_code}"
							and variant_of = {variant_of} and name in 
								(select parent from `tabItem Variant Attribute` 
								where attribute = "{attr_type}")
								;'''.format(item_code=item.item_code, variant_of=item.variant_of,
									attr_type=attr_type))

@frappe.whitelist()
def get_issue_items(**kwargs):
	data = []
	stock_entry = kwargs.get('stock_entry')
	if not stock_entry:
		return data
	items = frappe.get_doc("Stock Entry", stock_entry).items

	for entry_item in items:
		new_entry_item = frappe.new_doc("Stock Entry Detail")
		new_entry_item.item_code = entry_item.item_code
		new_entry_item.actual_qty = entry_item.actual_qty
		new_entry_item.valuation_rate = entry_item.valuation_rate
		new_entry_item.qty = entry_item.qty
		new_entry_item.retain_sample = entry_item.retain_sample
		new_entry_item.sample_quantity = entry_item.sample_quantity
		new_entry_item.cost_center = entry_item.cost_center
		new_entry_item.conversion_factor = entry_item.conversion_factor
		new_entry_item.stock_uom = entry_item.stock_uom
		new_entry_item.uom = entry_item.uom
		new_entry_item.transfer_qty = entry_item.transfer_qty
		new_entry_item.s_warehouse = entry_item.s_warehouse
		old_item = frappe.get_doc("Item", entry_item.item_code)

		if entry_item.ashbee_finished_item:
			finished_item = frappe.get_doc("Item", entry_item.ashbee_finished_item)
			new_entry_item.item_code = finished_item.item_code
			new_entry_item.valuation_rate = finished_item.valuation_rate
			new_entry_item.stock_uom = finished_item.stock_uom
		new_entry_item.basic_rate = new_entry_item.valuation_rate * new_entry_item.qty
		data.append(new_entry_item)
	return data

@frappe.whitelist()
def stock_entry_validate(doc, method):
	doc.ashbee_issue_items = ""
