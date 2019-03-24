


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

