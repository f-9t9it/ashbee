frappe.ui.form.on('Timesheet', {
	refresh: function (frm) {
		frm.trigger("_create_salary_slip_button");
	},
	_create_salary_slip_button: function (frm) {
		frm.remove_custom_button("Make Salary Slip");

		// from ERPNext's timesheet.js
		if (!frm.doc.salary_slip && frm.doc.employee) {
			frm.add_custom_button(
				__('Make Salary Slip'),
				function() { frm.trigger("_make_salary_slip"); },
				"fa fa-file-alt"
			);
		}
	},
	_make_salary_slip: async function (frm) {
		const { ashbee_ot1, ashbee_ot2 } = frm.doc;
		const { message: salary_slip } = await frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.timesheet.timesheet.make_salary_slip",
			frm,
		});
		salary_slip.ashbee_ot1 = ashbee_ot1;
		salary_slip.ashbee_ot2 = ashbee_ot2;

		if (ashbee_ot1 || ashbee_ot2) {
			await set_salary_detail_ots(
				salary_slip,
				ashbee_ot1,
				ashbee_ot2,
			);
		}
	}
});


frappe.ui.form.on('Timesheet Detail', {
	hours: function(frm, cdt, cdn) {
		set_ots(frm, cdt, cdn);
	},
	billable: function(frm, cdt, cdn) {
		set_ots(frm, cdt, cdn);
	},
	costing_rate: function(frm, cdt, cdn) {
		set_ots(frm, cdt, cdn);
	}
});


const set_salary_detail_ots = async function(salary_slip, ashbee_ot1, ashbee_ot2) {
	const salary_detail = frappe.model.add_child(salary_slip, "Salary Detail", "earnings");
	const overtime_component = await frappe.db.get_single_value("Ashbee Settings", "overtime");

	// overtime amounts
	const OT1 = 1.25;
	const OT2 = 1.50;

	const ashbee_ot1_amount = ashbee_ot1 * salary_slip.hour_rate * OT1;
	const ashbee_ot2_amount = ashbee_ot2 * salary_slip.hour_rate * OT2;

	salary_detail.salary_component = overtime_component;
	salary_detail.amount = ashbee_ot1_amount + ashbee_ot2_amount;
};

const set_ots = function(frm, cdt, cdn) {
	const child = locals[cdt][cdn];
	let ot = 0.0;
	let ot2 = 0.0;
	if(child.billable) {
		ot = child.hours * child.costing_rate * 1.25;
		ot2 = child.hours * child.costing_rate * 1.50;
	}
	child.ashbee_ot = ot;
	child.ashbee_ot2 = ot2;
	child.costing_amount = child.costing_amount + ot + ot2;
	refresh_field("ashbee_ot", child.name, "time_logs");
	refresh_field("ashbee_ot2", child.name, "time_logs");
	refresh_field("costing_amount", child.name, "time_logs");

	calculate_total_costing(frm, cdt, cdn);
};

const calculate_total_costing = function(frm, cdt, cdn){
	const child = locals[cdt][cdn];
	let total_costing = 0.0;
	let cl = frm.doc.time_logs || [];
	if(cl.length) {
		for (let i = 0; i < cl.length; i++) {
			total_costing = total_costing + cl[i]["costing_amount"]
		}
	}

	frm.doc.total_costing_amount = total_costing;
	frm.refresh_field("total_costing_amount");
};

