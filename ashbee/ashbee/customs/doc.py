import frappe
from frappe import _


def doc_save(doc, method):
    restricts = frappe.get_all(
        "Ashbee Settings Restrict",
        fields=["restrict_dt", "fieldname"]
    )
    restricts_data = {x.get("restrict_dt"): x.get("fieldname") for x in restricts}
    if doc.doctype not in restricts_data.keys():
        return
    _doc_save(doc, restricts_data.get(doc.doctype))


def _doc_save(doc, fieldname):
    project = doc.get(fieldname)
    project_status = frappe.db.get_value("Project", project, "status")
    if project_status in ["Completed", "Cancelled"]:
        frappe.throw(_("Transaction is not allowed. Project {} has already been {}".format(project, project_status)))
