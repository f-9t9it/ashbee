frappe.ui.form.on('Purchase Receipt', {
    currency: function(frm) {
        let currency = frm.doc.currency;
        frm.set_value('naming_series', currency === 'BHD' ? 'PRL-.YY.-.#####' : 'PRF-.YY.-.#####');
    }
})