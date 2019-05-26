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
    },
    ashbee_attribute_value: function(frm, cdt, cdn) {
        _set_ashbee_finished_item(frm, cdt, cdn);
    },
    ashbee_create_variant: function(frm, cdt, cdn) {
        _ash_create_variant(frm, cdt, cdn);
    }
});

var _set_ashbee_finished_item = function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
        child.ashbee_finished_item = "";

    refresh_field("ashbee_finished_item", child.name, "items");

    var _args = {
        'item_code': child.item_code,
        'attr_value': _extract_ashbee_attribute_value(child.ashbee_attribute_value),
        'attr_type': child.ashbee_attribute_type
    };

    frappe.call({
        method: "ashbee.ashbee.customs.stock_entry.get_finished_variant_item",
        args: _args,
        callback: function(r) {
            if(r.message) {
                child.ashbee_finished_item = r.message.name;
                child.ashbee_finished_item_valuation = parseFloat(r.message.rate);

                refresh_field("ashbee_finished_item", child.name, "items");
                refresh_field("ashbee_finished_item_valuation", child.name, "items");
            }
        }
    });
};

var _calculate_valuation_rate = function(args) {
    return (args.length * args.weight * args.added) + args.rate;
};

var _extract_ashbee_attribute_value = function(ashbee_attribute_value) {
    ashbee_attribute_value = ashbee_attribute_value.split("|")[1];
    return ashbee_attribute_value.trim();
};

var _confirm_variant_create_with_rate = function(frm, child, attrs_and_valuation) {
    var calculated = attrs_and_valuation.rate;

	if (child.ashbee_attribute_type === 'Colour') {
		calculated = _calculate_valuation_rate({
			length: attrs_and_valuation.Length,
			weight: attrs_and_valuation.weight,
			rate: attrs_and_valuation.rate,
			added: 0.250
		});
	}

	var fields = [
		{
			fieldname: "valuation_rate",
			label: __('Valuation Rate'),
			fieldtype: "Currency",
			default: attrs_and_valuation.rate,
			description: "Pre-calculated value",
			read_only: 1
		},
		{
			fieldname: "added_value",
			label: __('Added Value'),
			fieldtype: "Currency",
			default: 0.250,
			reqd: 1,
			onchange: function() {
				var calculated = _calculate_valuation_rate({
					length: attrs_and_valuation.Length,
					weight: attrs_and_valuation.weight,
					rate: attrs_and_valuation.rate,
					added: d.get_values().added_value
				});
				d.set_value('calculated_valuation_rate', calculated);
			}
		},
		{
			fieldname: "calculated_valuation_rate",
			label: __('Calculated Valuation Rate'),
			fieldtype: "Currency",
			default: calculated,
			description: "Calculated value",
			read_only: 1
		}
	];

	var d = new frappe.ui.Dialog({
		title: "Create Variant",
		fields: fields,
		primary_action_label: __('Create Variant'),
		primary_action: () => {
			d.get_primary_btn().attr('disabled', true);

			var _args = {
				"item_code": child.item_code,
				"added_value": d.get_values().added_value,
				"valuation_rate": d.get_values().valuation_rate,
				"attr_value": _extract_ashbee_attribute_value(child.ashbee_attribute_value),
				"attr_type": child.ashbee_attribute_type
			};

			if(_args) {
				frappe.call({
					method: "ashbee.ashbee.customs.stock_entry.create_variant_item",
					args: _args,
					callback: function(r){
						if(r.message){
							d.hide();
							frappe.show_alert("Items Updated!");
							child.ashbee_attribute_value = "";
							refresh_field("ashbee_attribute_value", child.name, "items");
						}
					}
				});
			}
		}
	});
	d.show();
};

var _ash_create_variant = function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    frappe.call({
		method: "ashbee.ashbee.customs.stock_entry.get_all_variant_attributes_and_rate",
		args: { "item_code": child.item_code },
		callback: function(r) {
			if(r && r.message) {
				_confirm_variant_create_with_rate(frm, child, r.message);
			}
		}
	});
};

var _make_custom_button = function(frm) {
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

                if (frm.doc.ashbee_production_issue) {
                    se_item.ashbee_recipient_task = 'Color Coating';
                    se_item.ashbee_attribute_type = item.ashbee_attribute_type;
                    se_item.ashbee_attribute_value = item.ashbee_attribute_value;
                    se_item.ashbee_finished_item = item.ashbee_finished_item;
                    se_item.ashbee_finished_item_valuation = item.ashbee_finished_item_valuation;
                }
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
