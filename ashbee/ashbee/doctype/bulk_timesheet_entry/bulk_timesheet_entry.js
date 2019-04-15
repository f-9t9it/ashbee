// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Timesheet Entry', {
	refresh: function(frm) {
		if(frm.doc.start_date_time == null){
			frm.doc.start_date_time = frappe.datetime.get_today();
			frm.refresh_field("start_date_time");
		}
	},

	employee:function(frm){
		frm.call({
			method:"get_employee_name",
			doc:frm.doc,
			callback:function(r){
				frm.doc.employee_name = r.message;
				frm.refresh_field("employee_name");
			}
		});
	},

	project:function(frm){
		frm.call({
			method:"get_project_name",
			doc:frm.doc,
			callback:function(r){
				frm.doc.project_name = r.message;
				frm.refresh_field("project_name")
			}
		});
	}
});
