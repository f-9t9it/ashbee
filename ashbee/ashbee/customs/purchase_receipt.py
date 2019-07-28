from ashbee.utils import set_item_weight, set_total_weight


def purchase_receipt_save(doc, method):
    set_item_weight(doc)
    set_total_weight(doc)
