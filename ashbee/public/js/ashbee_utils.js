frappe.provide('ashbee');

ashbee.populate_attribute_values = function(frm, cdt, cdn) {
    const child = locals[cdt][cdn];
    frappe.call({
        method: 'ashbee.ashbee.customs.stock_entry.get_attribute_values',
        args: {
            'item_code': child.item_code,
            'attr_type': child.ashbee_attribute_type
        },
        callback: function(r) {
            const options = $.map(r.message, _generate_attribute_values);
            _set_attribute_value_options(frm, child.name, options);
        }
    });
};

const _set_attribute_value_options = function(frm, child_name, options) {
    frm.set_df_property('ashbee_attribute_value', 'options', options.join('\n'), child_name, 'items');    refresh_field('ashbee_attribute_value', child_name, 'items');
};

const _generate_attribute_values = function(attr) {
    return attr[0] + " | " + attr[1];
};