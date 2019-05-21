frappe.ui.form.on('Material Request Item', {
    item_code: function(frm, cdt, cdn) {
        if (frm.doc.ashbee_production_issue) {
            frappe.model.set_value(cdt, cdn, 'ashbee_attribute_type', 'Colour');
        }
    },
    ashbee_attribute_type: function(frm, cdt, cdn) {
        ashbee_attribute_values_populate(frm, cdt, cdn);
    }
});

var ashbee_attribute_values_populate = function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    frappe.call({
        method: 'ashbee.ashbee.customs.stock_entry.get_attribute_values',
        args: { 'item_code': child.item_code, 'attr_type': child.ashbee_attribute_type },
        callback: function(r) {
            var attrs = $.map(r.message, _generate_attribute_values);
            frm.set_df_property('ashbee_attribute_value', 'options', attrs.join('\n'), child.name, 'items');
            refresh_field('ashbee_attribute_value', child.name, 'items');
        }
    });
};

var _generate_attribute_values = function(attr) {
    return attr[0] + " | " + attr[1];
};
