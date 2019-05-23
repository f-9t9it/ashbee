var ashbee_finished_item_populate = function(frm){
	frm.set_query("ashbee_finished_item","items", function(doc,cdt,cdn) {
			var child = locals[cdt][cdn];
				return {
					query:"ashbee.ashbee.customs.stock_entry.get_variant_items",
					filters: {
						'item_code':child.item_code,
						'attr_type':child.ashbee_attribute_type

					}
				};
			});
};

var ashbee_attribute_values_populate = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	if(child.ashbee_recipient_task != ""){
			frappe.call({
			method:"ashbee.ashbee.customs.stock_entry.get_attribute_values",
			args:{'item_code':child.item_code, 'attr_type':child.ashbee_attribute_type},
			callback:function(r){
				var m = [];
				$(r.message).each(function(i,v){
					m.push(v[0] + " | " +v[1]);
				});
				frm.set_df_property("ashbee_attribute_value", "options", m.join("\n"), child.name, "items");
				refresh_field("ashbee_attribute_value",child.name, "items");
			}
		});
	}	
};

var extract_ashbee_attribute_value = function(ashbee_attribute_value){
	ashbee_attribute_value = ashbee_attribute_value.split("|")[1];
	return ashbee_attribute_value.trim();
};

var set_ashbee_finished_item = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	child.ashbee_finished_item = "";
	refresh_field("ashbee_finished_item", child.name, "items");
	if(child.ashbee_recipient_task != ""){
		var _args = {
					'item_code':child.item_code,
					'attr_value':extract_ashbee_attribute_value(child.ashbee_attribute_value),
					'attr_type':child.ashbee_attribute_type
				}
		frappe.call({
			method:"ashbee.ashbee.customs.stock_entry.get_finished_variant_item",
			args:_args,
			callback:function(r){
				if(r.message){
					child.ashbee_finished_item = r.message.name;
					child.ashbee_finished_item_valuation = parseFloat(r.message.rate);
					
					refresh_field("ashbee_finished_item", child.name, "items");
					refresh_field("ashbee_finished_item_valuation", child.name, "items");
				}
			}
		});
	}
};

var ash_create_variant = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	frappe.call({
		method:"ashbee.ashbee.customs.stock_entry.get_all_variant_attributes_and_rate",
		args:{"item_code":child.item_code},
		callback:function(r){
			if(r && r.message){
				var rate = 0.0;
				var size = r.message["Size"] == undefined ? 0.0 : r.message["Size"];
				var weight = r.message['weight'] == undefined ? 0.0: r.message['weight'];
				if(child.ashbee_attribute_type == "Colour" || child.ashbee_attribute_type == "Color"){
					rate = (size * weight *0.250) + r.message.rate;
				}
				confirm_variant_create_with_rate(frm, child, rate, r.message);
			}
		}
	});
};

var confirm_variant_create_with_rate = function(frm, child, rate, attrs_and_valuation){
	var d = new frappe.ui.Dialog({
		title: "Create Variant",
		fields: [
			{ fieldname: "valuation_rate", label: __('Valuation Rate'), fieldtype: "Currency", default: rate },
			{ fieldname: "added_value", label: __('Added Value'), fieldtype: "Currency", default: 0.250, reqd: 1 }
		],
		primary_action_label: __('Create Variant'),
		primary_action: () => {
			d.get_primary_btn().attr('disabled', true);

			var _args = {
				"item_code": child.item_code,
				"added_value": d.get_values().added_value,
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

var set_page_primary_action = function(frm){
		var data = {};
		$.each(frm.doc.items, (i, v)=>{
			if(v.ashbee_recipient_task != "" && v.ashbee_attribute_type != "" && v.ashbee_attribute_value != ""
				&& v.ashbee_finished_item == "" && v.item_code != ""){

				frm.page.set_primary_action(__("Save"), function() {
			   		frappe.confirm(__("Create Variants and Save?"), function(){
			   			create_variants_and_save(frm);
			   			return false;

			   		});
		       });
			}
		});

};

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

var refresh_all_child_fields = function(frm){
	$.each(frm.doc.items, (i, v)=>{
		ashbee_attribute_values_populate(frm, v.doctype, v.name);
		set_ashbee_finished_item(frm, v.doctype, v.name);
	});
};

var make_receipt_button = function(frm) {
    if(frm.doc.docstatus === 1 && frm.doc.purpose === "Material Issue") {
        frm.add_custom_button(__('Make Receipt'), function() {
            frappe.model.with_doctype('Stock Entry', function() {
                var se = frappe.model.get_new_doc('Stock Entry');
                se.purpose = "Material Receipt";

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

var empty_child_fields = function(frm, cdt, cdn){
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


var set_color_coating_select = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	if(child.ashbee_recipient_task == "Color Coating"){
		child.ashbee_attribute_type = "Colour";
		refresh_field("ashbee_attribute_type", child.name, "items");
		ashbee_attribute_values_populate(frm, cdt, cdn);
	}
};


frappe.ui.form.on('Stock Entry Detail',{

	ashbee_attribute_type:function(frm, cdt, cdn){
		ashbee_attribute_values_populate(frm, cdt, cdn);
	},
	ashbee_attribute_value:function(frm, cdt, cdn){
		set_ashbee_finished_item(frm, cdt, cdn);
	},
	ashbee_recipient_task:function(frm, cdt, cdn){
		empty_child_fields(frm, cdt, cdn);
		set_color_coating_select(frm, cdt, cdn);
	},

	item_code:function(frm, cdt, cdn){
		empty_child_fields(frm, cdt, cdn);
	},

	ashbee_create_variant:function(frm, cdt, cdn){
		ash_create_variant(frm, cdt, cdn);

	},

});

frappe.ui.form.on('Stock Entry',{

	setup: function(frm) {
		frm.set_query("ashbee_issue_items", function() {
			return {
				filters: {
					'purpose': 'Material Issue',
					'docstatus':1
				}
			};
		});
	},

	refresh:function(frm){
		set_page_primary_action(frm);
        make_receipt_button(frm);
	},

	ashbee_issue_items:function(frm){
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
						row.ashbee_recipient_task = ""
						row.stock_uom = val.stock_uom
						row.uom = val.uom
						row.conversion_factor = val.conversion_factor
						row.cost_center = val.cost_center
						row.valuation_rate = val.valuation_rate
						row.transfer_qty = val.transfer_qty
						row.retain_sample = val.retain_sample
						row.sample_quantity = val.sample_quantity
						row.t_warehouse = val.s_warehouse
						refresh_field("items");
					});
				}
			}
		});
	}
});

