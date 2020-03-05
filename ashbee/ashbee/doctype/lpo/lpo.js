// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('LPO', {
	onload: function(frm) {
		frm.trigger('setup_queries');
		frm.set_query('account_head', 'taxes', function(doc) {
			var account_type = ['Tax', 'Chargeable', 'Income Account', 'Expenses Included in Valuation'];
			return {
				query: 'erpnext.controllers.queries.tax_account_query',
				filters: {
					'account_type': account_type,
					'company': doc.company
				}
			};
		});
	},
	supplier: function(frm) {
		frm.trigger('setup_queries');
	},
	refresh: function(frm) {
		if (frm.doc.taxes[0]) {
			const cdt = frm.doc.taxes[0].doctype;
			const cdn = frm.doc.taxes[0].name;
			_setup_tax_fields(frm, cdt, cdn);
		}
	},
	supplier_address: function(frm) {
		if (!frm.doc.supplier_address)
			return;

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
		_update_vat_amount(frm, cdt, cdn);
		_update_total_amount(frm);
		_update_total_qty(frm);
		frm.refresh();
	},
	qty: function(frm, cdt, cdn) {
		_update_amount(frm, cdt, cdn);
		_update_vat_amount(frm, cdt, cdn);
		_update_total_amount(frm);
		_update_total_qty(frm);
		frm.refresh();
	},
	vat_percentage: function(frm, cdt, cdn) {
	    _update_vat_amount(frm, cdt, cdn);
	    _update_total_amount(frm);
	    frm.refresh();
	},
	account_head: function(frm, cdt, cdn) {
		_update_description(frm, cdt, cdn);
	}
});

frappe.ui.form.on('Purchase Taxes and Charges', {
	charge_type: function(frm, cdt, cdn) {
		_setup_tax_fields(frm, cdt, cdn);
	}
});

var _update_description = function(frm, cdt, cdn) {
	var tax = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, 'description', tax.account_head);
};

var _setup_tax_fields = function(frm, cdt, cdn) {
	var tax = locals[cdt][cdn];
	var df = frappe.meta.get_docfield('Purchase Taxes and Charges', 'rate', frm.doc.name);
	df.read_only = tax.charge_type === "Actual" ? 1 : 0;
	refresh_field('taxes');
};

var _update_amount = function(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, 'amount', item.rate * item.qty);
	frm.refresh_field('items');
};

var _update_total_amount = function(frm) {
	var total = 0.00;
    var vat_total = 0.00;

	$.each(frm.doc.items, function(i, v) {
		total = total + v.amount;
		vat_total = vat_total + v.vat_amount;
	});

	frm.set_value('total', total);
	frm.set_value('base_total', total);
	frm.set_value('vat_total', vat_total);
	frm.set_value('net_total', total + vat_total);
	frm.set_value('base_net_total', total + vat_total);
};

var _update_total_qty = function(frm) {
	var total = 0;

	$.each(frm.doc.items, function(i, v) {
		total = total + v.qty;
	});

	frm.set_value('total_qty', total);
};

var _update_vat_amount = function(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, 'vat_amount', item.rate * item.qty * (item.vat_percentage / 100.00));
	frm.refresh_field('items');
};
