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
    latest_valuation_rate = first(
        frappe.get_all(
            'Stock Ledger Entry',
            filters=[['item_code', 'in', variants]],
            fields=['valuation_rate'],
        )
    )
    if latest_valuation_rate:
        valuation_rate = latest_valuation_rate.get('valuation_rate')
    return valuation_rate
