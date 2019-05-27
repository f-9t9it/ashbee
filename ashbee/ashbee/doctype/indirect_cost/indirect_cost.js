// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Indirect Cost', {
	posting_date: function(frm) {
		var start_date = moment(frm.doc.posting_date).startOf("month").format();
		var end_date = moment(frm.doc.posting_date).endOf("month").format();

		frm.set_value('start_date', start_date);
		frm.set_value('end_date', end_date);
	}
});
