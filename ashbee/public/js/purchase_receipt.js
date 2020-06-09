frappe.ui.form.on('Purchase Receipt', {
    currency: function(frm) {
        let currency = frm.doc.currency;
        frm.set_value('naming_series', currency === 'BHD' ? 'PRL-.YY.-.#####' : 'PRF-.YY.-.#####');
    },
    company: function(frm) {
      frm.set_query("project", "items", function() {
        return {
          filters: { company: frm.doc.company }
        };
      });
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
    },
    show_stock_ledger: function(frm) {
      var me = this;
      if (this.frm.doc.docstatus === 1) {
        cur_frm.add_custom_button(__("Stock Ledger"), function() {
          frappe.route_options = {
            voucher_no: me.frm.doc.name,
            from_date: me.frm.doc.posting_date,
            to_date: me.frm.doc.posting_date
          };
          frappe.set_route("query-report", "Ashbee Stock Movement");
        }, __("View"));
      }
    }
});

$.extend(cur_frm.cscript, new ashbee.stock.PurchaseReceiptController({ frm: cur_frm }));