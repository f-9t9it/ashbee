
var set_ots = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	var ot = 0.0;
	var ot2 = 0.0;
	if(child.billable){
		var ot = child.hours * child.costing_rate * 1.25;
		var ot2 = child.hours * child.costing_rate * 1.50;
	}
	child.ashbee_ot = ot;
	child.ashbee_ot2 = ot2;
	child.costing_amount = child.costing_amount + ot + ot2;
	refresh_field("ashbee_ot", child.name, "time_logs");
	refresh_field("ashbee_ot2", child.name, "time_logs");
	refresh_field("costing_amount", child.name, "time_logs");

	calculate_total_costing(frm, cdt, cdn);
}

var calculate_total_costing = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	var total_costing = 0.0;
	var cl = frm.doc.time_logs || [];
	if(cl.length){
		for (var i = 0; i < cl.length; i++) {
			total_costing = total_costing + cl[i]["costing_amount"]
		}
	}

	frm.doc.total_costing_amount = total_costing;
	frm.refresh_field("total_costing_amount");
}


frappe.ui.form.on('Timesheet Detail',{

	hours:function(frm, cdt, cdn){
		set_ots(frm, cdt, cdn);
	},

	billable:function(frm, cdt, cdn){
		set_ots(frm, cdt, cdn);
	},

	costing_rate:function(frm, cdt, cdn){
		set_ots(frm, cdt, cdn);
	}

});