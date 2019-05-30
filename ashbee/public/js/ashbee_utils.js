frappe.provide('ashbee');

const ATTRIBUTE_TYPES = {};

ashbee.populate_attribute_values = function(frm, cdt, cdn) {
    const child = locals[cdt][cdn];
    const item_code = child.item_code;
    const attr_type = child.ashbee_attribute_type;

    _get_attribute_values(item_code, attr_type, function(options) {
        _set_attribute_value_options(frm, child.name, options);
    });
};


ashbee.populate_attribute_values_rows_options = function(frm) {
    const items = frm.doc.items;

    items.forEach(function(item) {
        const attr_type = item.ashbee_attribute_type;
        if (_is_cached_type(attr_type)) {
            const options = ATTRIBUTE_TYPES[attr_type];
            _set_attribute_value_options(frm, item.name, options);
        } else {
            const item_code = item.item_code;
            _get_attribute_values(item_code, attr_type, function(options) {
                _set_attribute_value_options(frm, item.name, options);
            });
        }
    });
};


const _get_attribute_values = function(item_code, attr_type, fn) {
    frappe.call({
        method: 'ashbee.ashbee.customs.stock_entry.get_attribute_values',
        args: {
            'item_code': item_code,
            'attr_type': attr_type
        },
        callback: function(r) {
            ATTRIBUTE_TYPES[attr_type] = $.map(r.message, _generate_attribute_values);
            fn(ATTRIBUTE_TYPES[attr_type]);
        }
    });
};

const _set_attribute_value_options = function(frm, child_name, options) {
    frm.set_df_property('ashbee_attribute_value', 'options', options.join('\n'), child_name, 'items');
    refresh_field('ashbee_attribute_value', child_name, 'items');
};


const _generate_attribute_values = function(attr) {
    return attr[0] + " | " + attr[1];
};


const _is_cached_type = function(type) {
    return type in ATTRIBUTE_TYPES;
};
