import json
import frappe
from frappe.utils import flt
from erpnext.controllers.item_variant import get_variant, create_variant



# def printmsg(msglist):
# 	print("=="*8)
# 	print("\n"*8)
# 	for i in msglist:
# 		print(i)
# 	print("\n"*8)
# 	print("=="*8)

def check_and_create_attribute(item):
	item = frappe.get_doc("Item", item)
	return item

def get_variant_attribute_args(item, _args):
	args = {}
	for attr in item.attributes:
		args[attr.attribute] = attr.attribute_value
	args.update(_args)
	return _args

@frappe.whitelist()
def create_multiple_variants(**filters):
	variants = []
	for k,v in filters.items():
		if k == "cmd":
			continue
		v = json.loads(v);
		if not isinstance(v, dict):
			continue
		variant = create_variant_item(**v)
		variants.append({"cdn":v.get('cdn'),"variant":variant})
	return variants



@frappe.whitelist()
def create_variant_item(**filters):
	if not filters.get("item_code") or not filters.get("attr_type") or not filters.get("attr_value"):
		return
	item = frappe.get_doc("Item", filters.get("item_code"))
	if not item.variant_of:
		return
	args = {filters.get('attr_type'):filters.get("attr_value")}
	args = get_variant_attribute_args(item, args)
	variant = get_variant(item.variant_of, args)
	if variant:
		variant = frappe.get_doc("Item", variant)
	else:
		template = check_and_create_attribute(item.variant_of)
		variant = create_variant(template.name, args)
		make_variant_item_code(template.item_code, template.item_name, variant)
		variant.valuation_rate = 0.0
	if filters.get('valuation_rate'):
		variant.valuation_rate = filters.get('valuation_rate')
	variant.save();
	return variant


@frappe.whitelist()
def get_finished_variant_item(**filters):
	if not filters.get("item_code") or not filters.get("attr_type") or not filters.get("attr_value"):
		return
	item = frappe.get_doc("Item", filters.get("item_code"))
	if not item.variant_of:
		return
	variant = get_variant(item.variant_of, {filters.get("attr_type"):filters.get("attr_value")})
	if variant:
		variant = frappe.get_doc("Item", variant)
		return {'name':variant.name, 'rate':variant.valuation_rate}




@frappe.whitelist()
def get_attribute_values(**filters):
	if not filters.get("item_code") or not filters.get("attr_type"):
		return []
	item = frappe.get_doc("Item", filters.get("item_code"))
	if not item.variant_of:
		return []
	attr_type = filters.get("attr_type")
	return frappe.db.sql('''select attribute_value from `tabItem Attribute Value`
							where parent = '{parent}' and parenttype = 'Item Attribute'; '''
							.format(parent=attr_type),as_list = 1)

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
			new_entry_item.valuation_rate = flt(entry_item.ashbee_finished_item_valuation)
			new_entry_item.stock_uom = finished_item.stock_uom
		new_entry_item.basic_rate = new_entry_item.valuation_rate * new_entry_item.qty
		data.append(new_entry_item)
	return data


def make_variant_item_code(template_item_code, template_item_name, variant):
	"""Uses template's item code and abbreviations to make variant's item code"""
	if variant.item_code:
		return

	abbreviations = []
	for attr in variant.attributes:
		item_attribute = frappe.db.sql("""select i.numeric_values, v.abbr
			from `tabItem Attribute` i left join `tabItem Attribute Value` v
				on (i.name=v.parent)
			where i.name=%(attribute)s and (v.attribute_value=%(attribute_value)s or i.numeric_values = 1)""", {
				"attribute": attr.attribute,
				"attribute_value": attr.attribute_value
			}, as_dict=True)

		if not item_attribute:
			continue
			# frappe.throw(_('Invalid attribute {0} {1}').format(frappe.bold(attr.attribute),
			# 	frappe.bold(attr.attribute_value)), title=_('Invalid Attribute'),
			# 	exc=InvalidItemAttributeValueError)

		abbr_or_value = cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].abbr
		abbreviations.append(abbr_or_value)

	if abbreviations:
		variant.item_code = "{0}-{1}".format(template_item_code, "-".join(abbreviations))
		variant.item_name = "{0}-{1}".format(template_item_name, "-".join(abbreviations))

