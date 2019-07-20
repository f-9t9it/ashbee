// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Central Expense', {
	refresh: function(frm) {
		_set_posting_date(frm);
	}
});


var _set_posting_date = function(frm) {
	if (frm.doc.__islocal) {
		frm.set_value('posting_date', frappe.datetime.now_date());
	}
};
