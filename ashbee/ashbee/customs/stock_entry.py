import json
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.controllers.item_variant import get_variant, create_variant
from ashbee.utils import get_central_entry, check_central_expense


def stock_entry_save(doc, method):
    check_central_expense(doc.posting_date)
    _check_receipt_existed(doc)
    _set_finished_items(doc)

    _set_item_weight(doc)
    _set_total_weight(doc)

    if doc.naming_series == "SE-PI-.#####":
        any(_set_item_recipient_task_color_coating(item) for item in doc.items)


def stock_entry_submit(doc, method):
    _check_item_already_issued(doc)
    _set_central_entry(doc)
    _set_material_return_in_project(doc)


def stock_entry_cancel(doc, method):
    _cancel_central_entry(doc)


def _check_receipt_existed(doc):
    validate_material_issue = frappe.db.get_single_value(
        'Ashbee Settings',
        'validate_material_issue'
    )

    if not validate_material_issue:
        return

    if doc.purpose == 'Material Receipt':
        filters = {
            'ashbee_material_issue': doc.ashbee_material_issue,
            'docstatus': 1
        }

        material_receipts = frappe.get_all('Stock Entry', filters)

        if material_receipts:
            frappe.throw(_('Existing Material Receipt found for {}'.format(doc.ashbee_material_issue)))


def _set_finished_items(doc):
    for item in doc.items:
        _set_finished_item(item)


def _set_item_weight(doc):
    for item in doc.items:
        weight = frappe.db.get_value('Item', item.item_code, 'ashbee_weight')
        length = _get_item_length(item.item_code)
        item.item_weight = weight * length
        item.ashbee_item_weight = item.item_weight * item.qty


def _get_item_length(item):
    filters = {'parent': item, 'attribute': 'Length'}

    item_length = frappe.db.sql("""
        SELECT attribute_value
        FROM `tabItem Variant Attribute`
        WHERE parent = %(parent)s AND attribute = %(attribute)s
    """, filters, as_list=True)

    return float(item_length[0][0]) if item_length else 0.00


def _set_total_weight(doc):
    total_weight = 0.00
    for item in doc.items:
        total_weight = total_weight + item.ashbee_item_weight
    doc.ashbee_total_weight = total_weight


def _set_finished_item(item):
    if item.ashbee_recipient_task:
        item_for_creation = {
            'item_code': item.item_code,
            'attr_value': _extract_attribute_value(item.ashbee_attribute_value),
            'attr_type': item.ashbee_attribute_type
        }

        variant_item = get_finished_variant_item(**item_for_creation)

        if variant_item:
            variant_item['valuation_rate'] = variant_item.pop('rate')
        else:
            variant_item = create_variant_item(**item_for_creation)

        item.ashbee_finished_item = variant_item.get('name')
        item.ashbee_finished_item_valuation = variant_item.get('valuation_rate')


def _extract_attribute_value(attribute_value):
    extracted_value = attribute_value.split('|')[1]
    return extracted_value.strip()


def _check_item_already_issued(doc):
    if not doc.ashbee_is_return:
        return

    validate_material_return = frappe.db.get_single_value('Ashbee Settings', 'validate_material_return')

    if not validate_material_return:
        return

    for item in doc.items:
        sle = frappe.db.sql("""
            SELECT count(*) AS items_count FROM `tabStock Ledger Entry` AS sle
            WHERE sle.item_code=%s AND sle.project=%s
        """, (item.item_code, doc.project), as_dict=1)

        if sle['items_count'] == 0:
            frappe.throw(
                _('Item {} was not issued to Project {}'.format(item.item_code, doc.project))
            )


def _cancel_central_entry(doc):
    central_entry = get_central_entry(doc.name)

    if central_entry:
        central_entry.cancel()


def _set_central_entry(doc):
    central_project = frappe.db.get_single_value('Ashbee Settings', 'central_project')
    if doc.purpose == 'Material Issue' and not doc.ashbee_central_entry:
        if doc.project == central_project:
            central_entry = _create_central_entry(doc)
            central_entry.submit()


def _create_central_entry(doc):
    # TODO: use the create_central_entry from utils.py
    return frappe.get_doc({
        'doctype': 'Central Entry',
        'posting_date': doc.posting_date,
        'voucher_type': 'Stock Entry',
        'voucher_no': doc.name,
        'allocation': doc.total_amount
    }).insert()


def _set_material_return_in_project(doc):
    if doc.purpose == 'Material Issue' and doc.ashbee_is_return:
        if doc.project:
            total_material_return = _get_total_material_return(doc.project)
            material_returns = sum([item.qty for item in doc.items])
            _set_total_material_return(doc.project, total_material_return + material_returns)


def _set_item_recipient_task_color_coating(item):
    item.ashbee_recipient_task = "Color Coating"


def _get_total_material_return(project):
    return frappe.db.get_value('Project', project, 'ashbee_total_material_return')


def _set_total_material_return(project, total_material_return):
    frappe.db.set_value('Project', project, 'ashbee_total_material_return', total_material_return)


@frappe.whitelist()
def calculate_valuation_rate(length, width, added, rate):
    return (length * width * added) + rate


@frappe.whitelist()
def get_all_variant_attributes_and_rate(item_code):
    item = frappe.get_doc("Item", item_code)
    attrs = {}
    if not item.attributes:
        return None
    for attr in item.attributes:
        attrs[attr.attribute] = attr.attribute_value
    attrs['rate'] = item.valuation_rate
    attrs['weight'] = get_weight_from_item(item)
    return attrs


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

    args = {filters.get('attr_type'): filters.get("attr_value")}
    args = get_variant_attribute_args(item, args)
    variant = get_variant(item.variant_of, args)

    if variant:
        variant = frappe.get_doc("Item", variant)
    else:
        template = check_and_create_attribute(item.variant_of)
        args = update_missing_variant_attrs(item, template, args)
        variant = create_variant(template.name, args)
        weight = get_weight_from_item(item)
        # variant.valuation_rate = frappe.db.get_value('Item', item.variant_of, 'valuation_rate')
        variant.valuation_rate = item.valuation_rate
        variant.ashbee_weight = weight

    variant.save()
    return variant


def update_missing_variant_attrs(item, template, args):
    template_attrs = {attr.attribute:attr.attribute_value for attr in template.attributes}
    item_attrs = {attr.attribute:attr.attribute_value for attr in item.attributes}
    _args = {}
    for attr in template_attrs.keys():
        if attr not in args.keys():
            _args[attr] = item_attrs[attr]
        else:
            _args[attr] = args[attr]
    return _args


def get_size_from_item(item):
    for attr in item.attributes:
        if attr.attribute == "Size":
            return flt(attr.attribute_value)
    return 0.0


def get_weight_from_item(item):
    if isinstance(item ,str):
        item = frappe.get_doc("Item", item)
    if item.ashbee_bar:
        return item.ashbee_weight
    return item.weight_per_unit


def get_length_from_item(item):
    for attr in item.attributes:
        if attr.attribute == "Length":
            return flt(attr.attribute_value)
    return 0.0


@frappe.whitelist()
def get_finished_variant_item(**filters):
    if not filters.get("item_code") or not filters.get("attr_type") or not filters.get("attr_value"):
        return
    item = frappe.get_doc("Item", filters.get("item_code"))
    if not item.variant_of:
        return
    template = frappe.get_doc("Item",item.variant_of)
    args = update_missing_variant_attrs(item, template, {filters.get("attr_type"):filters.get("attr_value")})
    variant = get_variant(item.variant_of, args)
    if variant:
        variant = frappe.get_doc("Item", variant)
        return {'name': variant.name, 'rate': variant.valuation_rate}


@frappe.whitelist()
def get_attribute_values(**filters):
    if not filters.get("item_code") or not filters.get("attr_type"):
        return []
    item = frappe.get_doc("Item", filters.get("item_code"))
    if not item.variant_of:
        return []
    attr_type = filters.get("attr_type")

    return frappe.db.sql("""
        SELECT abbr, attribute_value FROM `tabItem Attribute Value`
        WHERE parent=%s AND parenttype="Item Attribute"
        ORDER BY CAST(abbr AS UNSIGNED) ASC
    """, attr_type, as_list=1)


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


@frappe.whitelist()
def get_attribute_values_by_name(name):
    item_attribute = frappe.db.sql("""
        SELECT attribute_value, abbr
        FROM `tabItem Attribute Value`
        WHERE name=%s
    """, name, as_dict=1)
    return item_attribute[0] if item_attribute else None
