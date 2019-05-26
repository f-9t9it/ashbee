frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        _make_custom_button(frm);
    }
});

frappe.ui.form.on('Material Request Item', {
    items_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'project', frm.doc.project);
    },
    item_code: function(frm, cdt, cdn) {
        if (frm.doc.ashbee_production_issue) {
            frappe.model.set_value(cdt, cdn, 'ashbee_attribute_type', 'Colour');
        }
    },
    ashbee_attribute_type: function(frm, cdt, cdn) {
        ashbee_attribute_values_populate(frm, cdt, cdn);
    }
});

var _make_custom_button = function(frm) {
    if (frm.doc.material_request_type !== 'Material Issue')
        return;

    frm.add_custom_button(__('Make Issue'), function() {
        frappe.model.with_doctype('Stock Entry', function() {
            var se = frappe.model.get_new_doc('Stock Entry');
            se.purpose = 'Material Issue';

            var items = frm.doc.items;
            items.forEach(function(item) {
                var se_item = frappe.model.add_child(se, 'items');
                    se_item.item_code = item.item_code;
                    se_item.basic_rate = item.rate;
                    se_item.item_name = item.item_name;
                    se_item.uom = item.uom;
                    se_item.conversion_factor = item.conversion_factor;
                    se_item.item_group = item.item_group;
                    se_item.description = item.description;
                    se_item.image = item.image;
                    se_item.qty = item.qty;
                    se_item.transfer_qty = item.qty;
                    se_item.warehouse = item.warehouse;
                    se_item.required_date = frappe.datetime.nowdate();
            });

            frappe.set_route('Form', 'Stock Entry', se.name);
        });
    })
};

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
