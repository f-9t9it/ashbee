frappe.provide('ashbee.buying');

ashbee.buying.PurchaseOrderController = erpnext.buying.PurchaseOrderController.extend({
    onload: function(frm) {
        this._super();
        this.frm.set_query('item_code', 'items', function() {
            return { query: 'ashbee.queries.item_query' };
        });
    },
    items_add: function(doc, cdt, cdn) {
        if (!doc.project) {
            return;
        }
        frappe.model.set_value(cdt, cdn, 'project', doc.project);
    }
});

$.extend(cur_frm.cscript, new ashbee.buying.PurchaseOrderController({ frm: cur_frm }));