frappe.provide('ashbee.stock');

frappe.ui.form.on('Stock Entry', {
	onload: function(frm) {
		frm.set_query("ashbee_attribute_fetch", "items", function(doc, cdt, cdn) {
			var attribute_type = locals[cdt][cdn].ashbee_attribute_type;
			return { filters: { parent: attribute_type } };
		});
		frm.set_query("item_code", "items", function() {
			return { query: "ashbee.queries.item_query" };
		});
		frm.set_df_property("ashbee_attribute_fetch", "ignore_link_validation", 1, frm.doc.name, "items");
	},
	setup: function(frm) {
		frm.set_query("ashbee_issue_items", function() {
			return {
				filters: {
					'purpose': 'Material Issue',
					'docstatus': 1,
					'ashbee_production_issue': 1
				}
			};
		});
		frm.set_query("ashbee_material_issue", function() {
			return {
				filters: {
					'purpose': 'Material Issue',
					'docstatus': 1,
					'ashbee_production_issue': 1
				}
			};
		});
	},
	refresh: function(frm) {
		frm.trigger('naming_series');
		// _set_page_primary_action(frm);
        _make_receipt_button(frm);
        _populate_rows_attribute_values(frm);
	},
	ashbee_production_issue: function(frm) {
		_set_naming_series(frm);
	},
	purpose: function(frm) {
		if (frm.doc.purpose === "Material Issue") {
            frm.set_value('naming_series', 'MI-.YY.-.#####');
        } else if (frm.doc.purpose === "Material Return") {
		    frm.set_value('naming_series', 'MR-.YY.-.#####');
        }
	},
	naming_series: function(frm) {
		const series = ['MI-.YY.-.#####', 'MR-.YY.-.#####'];

		frm.set_df_property(
			'project',
			'reqd',
			series.includes(frm.doc.naming_series) ? 1 : 0
		);

		frm.set_df_property(
			'ashbee_project_ref',
			'hidden',
			series.includes(frm.doc.naming_series) ? 1 : 0
		);

		_setup_project_field(frm);
	},
	ashbee_issue_items: function(frm) {
		var args = {"stock_entry":frm.doc.ashbee_issue_items};
		return frappe.call({
			method: "ashbee.ashbee.customs.stock_entry.get_issue_items",
			args,
			callback:function(r){
				if(r.message){
					frm.clear_table("items");
					$.each(r.message, function(i, val){
						var row = frm.add_child("items");
						row.item_code = val.item_code;
						row.qty = val.qty;
						row.ashbee_recipient_task = "";
						row.stock_uom = val.stock_uom;
						row.uom = val.uom;
						row.conversion_factor = val.conversion_factor;
						row.cost_center = val.cost_center;
						row.valuation_rate = val.valuation_rate;
						row.transfer_qty = val.transfer_qty;
						row.retain_sample = val.retain_sample;
						row.sample_quantity = val.sample_quantity;
						row.t_warehouse = val.s_warehouse;
						refresh_field("items");
					});
				}
			}
		});
	}
});


frappe.ui.form.on('Stock Entry Detail', {
	ashbee_attribute_type: function(frm, cdt, cdn) {
		ashbee.populate_attribute_values(frm, cdt, cdn);
	},
	ashbee_attribute_fetch: function(frm, cdt, cdn) {
		_set_attribute_value(frm, cdt, cdn);
	},
	ashbee_attribute_value: function(frm, cdt, cdn) {
		_set_ashbee_finished_item(frm, cdt, cdn);
	},
	ashbee_recipient_task: function(frm, cdt, cdn) {
		_empty_child_fields(frm, cdt, cdn);
		_set_color_coating_select(frm, cdt, cdn);
	},
	item_code: function(frm, cdt, cdn) {
		_empty_child_fields(frm, cdt, cdn);
		_set_attribute_type(frm, cdt, cdn);
	},
	ashbee_create_variant: function(frm, cdt, cdn) {
		_ash_create_variant(frm, cdt, cdn);
	},
});


var extract_ashbee_attribute_value = function(ashbee_attribute_value){
	ashbee_attribute_value = ashbee_attribute_value.split("|")[1];
	return ashbee_attribute_value.trim();
};


var _set_attribute_value = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];

	frappe.call({
		method: "ashbee.ashbee.customs.stock_entry.get_attribute_values_by_name",
		args: { name: child.ashbee_attribute_fetch },
		callback: function(r) {
			if(r.message) {
				const { attribute_value, abbr } = r.message;

				if (child.ashbee_attribute_type === "Colour") {
					child.ashbee_attribute_value = `${abbr} | ${attribute_value}`;
				}
				if (child.ashbee_attribute_type === "Length") {
					child.ashbee_attribute_value = `${attribute_value} | ${attribute_value}`;
				}

				refresh_field("ashbee_attribute_value", child.name, "items");
			}
		}
	});
};


var _setup_project_field = function(frm) {
	const series = ['MTSOUT-.YY.-.#####', 'MTSIN-.YY.-.#####'];

	frm.set_df_property(
		'project',
		'hidden',
		series.includes(frm.doc.naming_series) ? 1 : 0
	);

	frm.set_df_property(
		'ashbee_project_ref',
		'reqd',
		series.includes(frm.doc.naming_series) ? 1 : 0
	);

};


var _set_ashbee_finished_item = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	child.ashbee_finished_item = "";

	refresh_field("ashbee_finished_item", child.name, "items");

	if(child.ashbee_recipient_task != "") {
		var _args = {
			'item_code': child.item_code,
			'attr_value': extract_ashbee_attribute_value(child.ashbee_attribute_value),
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
	}
};


var _ash_create_variant = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	frappe.call({
		method: "ashbee.ashbee.customs.stock_entry.get_all_variant_attributes_and_rate",
		args: { "item_code": child.item_code },
		callback: function(r) {
			if(r && r.message) {
				confirm_variant_create_with_rate(frm, child, r.message);
			}
		}
	});
};


var calculate_valuation_rate = function(args) {
	return (args.length * args.weight * args.added) + args.rate;
};


var confirm_variant_create_with_rate = function(frm, child, attrs_and_valuation) {
	var calculated = attrs_and_valuation.rate;

	if (child.ashbee_attribute_type === 'Colour') {
		calculated = calculate_valuation_rate({
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
			read_only: 1
		},
	];

	var d = new frappe.ui.Dialog({
		title: "Create Variant",
		fields: fields,
		primary_action_label: __('Create Variant'),
		primary_action: () => {
			d.get_primary_btn().attr('disabled', true);

			var _args = {
				"item_code": child.item_code,
				"valuation_rate": d.get_values().valuation_rate,
				"attr_value": extract_ashbee_attribute_value(child.ashbee_attribute_value),
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

// DEPRECATED
// var _set_page_primary_action = function(frm){
// 		var data = {};
// 		$.each(frm.doc.items, (i, v)=>{
// 			if(v.ashbee_recipient_task != "" && v.ashbee_attribute_type != "" && v.ashbee_attribute_value != ""
// 				&& v.ashbee_finished_item == "" && v.item_code != ""){
//
// 				frm.page.set_primary_action(__("Save"), function() {
// 			   		frappe.confirm(__("Create Variants and Save?"), function(){
// 			   			create_variants_and_save(frm);
// 			   			return false;
//
// 			   		});
// 		       });
// 			}
// 		});
//
// };


var create_variants_and_save = function(frm){
	var attrs = [];
	$.each(frm.doc.items, (i, v)=>{
		if(v.ashbee_recipient_task != "" && v.ashbee_attribute_type != "" && v.ashbee_attribute_value != ""
				&& v.ashbee_finished_item == "" && v.item_code != ""){
			attrs.push({
						'cdn':v.name,
						'item_code':v.item_code, 
						'attr_type':v.ashbee_attribute_type, 
						'attr_value':extract_ashbee_attribute_value(v.ashbee_attribute_value)
					});
		}
		if((i+1) >= frm.doc.items.length && attrs.length > 0){
			frappe.call({
				method:"ashbee.ashbee.customs.stock_entry.create_multiple_variants",
				args:attrs,
				callback:function(r){
					if(r.message){
						$(r.message).each(function(i){
							var child = locals[v.doctype][this.cdn];
							child.ashbee_finished_item = this.variant.name;
							child.ashbee_finished_item_valuation = this.variant.valuation_rate
							refresh_field("ashbee_finished_item_valuation", child.name, "items");
							refresh_field("ashbee_finished_item", child.name, "items");
							if((i+1) >= r.message.length){
								frappe.show_alert("Items Updated!");
								frm.save();
								window.location.reload();
							}

						});

					}
				}
			});
		}
		
	});
};


var _make_receipt_button = function(frm) {
    if(frm.doc.docstatus === 1 && frm.doc.purpose === "Material Issue") {
        frm.add_custom_button(__('Make Receipt'), function() {
            frappe.model.with_doctype('Stock Entry', function() {
                var se = frappe.model.get_new_doc('Stock Entry');
                se.naming_series = "MTSIN-.YY.-.#####";
                se.purpose = "Material Receipt";
				se.ashbee_material_issue = frm.doc.name;

                var items = frm.get_field('items').grid.get_selected_children();
                if(!items.length) {
                    items = frm.doc.items;
                }

                items.forEach(function(item) {
                    var se_item = frappe.model.add_child(se, 'items');
                    se_item.item_code = item.ashbee_finished_item;
                    se_item.basic_rate = item.ashbee_finished_item_valuation;
                    se_item.item_name = item.item_name;
                    se_item.uom = item.uom;
                    se_item.conversion_factor = item.conversion_factor;
                    se_item.item_group = item.item_group;
                    se_item.description = item.description;
                    se_item.image = item.image;
                    se_item.qty = item.qty;
                    se_item.transfer_qty = item.transfer_qty;
                    se_item.warehouse = item.s_warehouse;
                    se_item.required_date = frappe.datetime.nowdate();
                });

                frappe.set_route('Form', 'Stock Entry', se.name);
            });
        });
    }
};


var _empty_child_fields = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	child.ashbee_finished_item = "";
	child.ashbee_attribute_type = "";
	child.ashbee_attribute_value = "";
	child.ashbee_finished_item_valuation = "";

	refresh_field("ashbee_finished_item_valuation", child.name, "items");
	refresh_field("ashbee_finished_item", child.name, "items");
	refresh_field("ashbee_attribute_type", child.name, "items");
	refresh_field("ashbee_attribute_value", child.name, "items");
};


var _set_color_coating_select = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];

	if (child.ashbee_recipient_task === 'Color Coating') {
		child.ashbee_attribute_type = "Colour";
		refresh_field("ashbee_attribute_type", child.name, "items");
		ashbee.populate_attribute_values(frm, cdt, cdn);
	}
};


let last_naming_series = '';
var _set_naming_series = function(frm) {
	let naming_series = !last_naming_series ? frm.doc.naming_series : '';

	if (frm.doc.ashbee_production_issue) {
		last_naming_series = frm.doc.naming_series;
		naming_series = 'MTSOUT-.YY.-.#####';
	} else {
		naming_series = last_naming_series;
	}

	frm.set_value('naming_series', naming_series);
};


var _set_attribute_type = function(frm, cdt, cdn) {
    if (frm.doc.ashbee_production_issue) {
        frappe.model.set_value(cdt, cdn, 'ashbee_attribute_type', 'Colour');
    }
};


var _populate_rows_attribute_values = function(frm) {
	if (!frm.doc.__islocal) {
		ashbee.populate_attribute_values_rows_options(frm);
	}
};

ashbee.stock.StockEntry = erpnext.stock.StockEntry.extend({
	show_stock_ledger: function() {
		var me = this;
		if (this.frm.doc.docstatus === 1) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: me.frm.doc.posting_date
				};
				frappe.set_route("query-report", "Ashbee Stock Movement");
			}, __("View"));
		}
	}
});

$.extend(cur_frm.cscript, new ashbee.stock.StockEntry({ frm: cur_frm }));
