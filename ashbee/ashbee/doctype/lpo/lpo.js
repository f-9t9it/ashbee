// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('LPO', {
	onload: function(frm) {
		frm.trigger('setup_queries');
	},
	refresh: function(frm) {

	},
	supplier_address: function(frm) {
		frappe.call({
			method: 'frappe.contacts.doctype.address.address.get_address_display',
			args: {'address_dict': frm.doc.supplier_address },
			callback: function(r) {
				if (r.message) {
					frm.set_value('address_display', r.message);
				}
			}
		});
	},
	shipping_address: function(frm) {
		erpnext.utils.get_address_display(frm, "shipping_address", "shipping_address_display", true);
	},
	setup_queries: function(frm) {
		frm.set_query('supplier_address', {
			query: 'frappe.contacts.doctype.address.address.address_query',
			filters: {
				link_doctype: 'Supplier',
				link_name: frm.doc.supplier
			}
		});
	}
});

frappe.ui.form.on('LPO Item', {
	rate: function(frm, cdt, cdn) {
		_update_amount(frm, cdt, cdn);
		_update_total_amount(frm);
		_update_total_qty(frm);
		frm.refresh();
	},
	qty: function(frm, cdt, cdn) {
		_update_amount(frm, cdt, cdn);
		_update_total_amount(frm);
		_update_total_qty(frm);
		frm.refresh();
	}
});

var _update_amount = function(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, 'amount', item.rate * item.qty);
	frm.refresh_field('items');
};

var _update_total_amount = function(frm) {
	var total = 0.00;

	$.each(frm.doc.items, function(i, v) {
		total = total + v.amount;
	});

	frm.set_value('total', total);
	frm.set_value('net_total', total);
	frm.set_value('base_total', total);
	frm.set_value('base_net_total', total);
};

var _update_total_qty = function(frm) {
	var total = 0;

	$.each(frm.doc.items, function(i, v) {
		total = total + v.qty;
	});

	frm.set_value('total_qty', total);
}