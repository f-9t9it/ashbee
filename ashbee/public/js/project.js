const OVERHEAD_MULTIPLIER = 0.20;

frappe.ui.form.on('Project', {
    refresh: function(frm) {
        _set_overhead_charges(frm);
        _set_project_code_read_only(frm);
    }
});

var _set_project_code_read_only = function(frm) {
    if (_check_form_for_read_only(frm)) return;
    frm.set_df_property('ashbee_project_code', 'read_only', 1);
};

var _set_overhead_charges = function(frm) {
    const costs = [
        frm.doc.total_costing_amount, // labour
        frm.doc.ashbee_total_direct_cost,
        frm.doc.total_consumed_material_cost, // stock entry
        frm.doc.ashbee_total_indirect_cost
    ];

    frm.set_value('ashbee_total_overhead_charges', costs.reduce(_compute_sum) * OVERHEAD_MULTIPLIER);
};

// helpers
var _compute_sum = function(total, num) {
    return total + num;
};

var _check_form_for_read_only = function(frm) {
    return frm.doc.__islocal
        || !frm.doc.ashbee_project_code
        || frappe.user_roles.includes('System Manager');
};
