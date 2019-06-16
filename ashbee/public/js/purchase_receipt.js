frappe.ui.form.on('Purchase Receipt', {
    currency: function(frm) {
        let currency = frm.doc.currency;
        frm.set_value('naming_series', currency === 'BHD' ? 'PRL-.YY.-.#####' : 'PRF-.YY.-.#####');
    }
});

// override
frappe.provide('ashbee.stock');

ashbee.stock.PurchaseReceiptController = erpnext.stock.PurchaseReceiptController.extend({
    onload: function(frm) {
        this._super();
        this.frm.set_query('item_code', 'items', function() {
            return { query: 'ashbee.queries.item_query' };
        });
    }
});

$.extend(cur_frm.cscript, new ashbee.stock.PurchaseReceiptController({ frm: cur_frm }));