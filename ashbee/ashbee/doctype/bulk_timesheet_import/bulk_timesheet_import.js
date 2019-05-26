// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Timesheet Import', {
	refresh: function(frm) {
		_create_custom_button(frm);
	}
});

var _create_custom_button = function(frm) {
	if (!frm.doc.bulk_timesheet_entry) return;
	frm.add_custom_button(__('Go to Entry'), function() {
		frappe.set_route('Form', 'Bulk Timesheet Entry', frm.doc.bulk_timesheet_entry);
	});
};
