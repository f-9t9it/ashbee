// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ashbee Settings', {
	create_central_entries: function(frm) {
		frm.call({
			doc: frm.doc,
			method: 'create_central_entries',
			callback: function(r) {
				console.log(r);
			}
		});
	}
});
