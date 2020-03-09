import frappe
from toolz import first


def get_latest_valuation_rate(item_code):
    """
    Get latest valuation rate
    :param item_code: [Item] must be a template
    :return:
    """
    valuation_rate = 0.00
    variants = map(
        lambda x: x['name'],
        frappe.get_all(
            'Item',
            filters={'variant_of': item_code}
        )
    )
    sl_entries = frappe.get_all(
        'Stock Ledger Entry',
        filters=[['item_code', 'in', variants]],
        fields=['valuation_rate'],
    )
    if sl_entries:
        latest_valuation_rate = first(sl_entries)
        valuation_rate = latest_valuation_rate.get('valuation_rate')
    return valuation_rate
