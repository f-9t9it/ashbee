// Copyright (c) 2019, 9t9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on("Direct Cost", {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.set_query("job_no", "items", function () {
        return { filters: { company: frm.doc.company } };
      });
    }
  },
  company: function (frm) {
    frm.set_query("job_no", "items", function () {
      return { filters: { company: frm.doc.company } };
    });
  },
});
