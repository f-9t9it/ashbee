# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ashbee"
app_title = "Ashbee"
app_publisher = "9t9IT"
app_description = "Ashbee Frappe App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "bomsy1@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/ashbee/css/ashbee.css"
# app_include_js = "/assets/ashbee/js/ashbee.js"

# include js, css files in header of web template
# web_include_css = "/assets/ashbee/css/ashbee.css"
# web_include_js = "/assets/ashbee/js/ashbee.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "public/js/stock_entry.js",
    "Timesheet": "public/js/timesheet.js",
    "Material Request": "public/js/material_request.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Project": "public/js/project.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Material Request Item-ashbee_attribute_type",
                    "Material Request Item-ashbee_attribute_value",
                    "Material Request-ashbee_production_issue",
                    "Material Request-project",
                    "Stock Entry Detail-ashbee_recipient_task",
                    "Employee-nationality",
                    "Employee-rp_expiry",
                    "Employee-cpr_expiry",
                    "Employee-cpr",
                    "Timesheet Detail-ashbee_ot",
                    "Timesheet Detail-ashbee_ot2",
                    "Timesheet Detail-ashbee_ot_col_brk",
                    "Timesheet Detail-ashbee_ot_sec_break",
                    "Project-ashbee_job_amount",
                    "Project-ashbee_job_col_brk1",
                    "Stock Entry Detail-ashbee_finished_item_valuation",
                    "Stock Entry Detail-ashbee_attribute_value",
                    "Stock Entry Detail-ashbee_create_variant",
                    "Stock Entry Detail-ashbee_finished_item",
                    "Stock Entry Detail-ashbee_col_1",
                    "Stock Entry Detail-ashbee_finished_sec",
                    "Print Settings-print_taxes_with_zero_amount",
                    "Print Settings-compact_item_print",
                    "Deleted Document-hub_sync_id",
                    "Item-hub_sync_id",
                    "Deleted Document-github_sync_id",
                    "Task-github_sync_id",
                    "Project-github_sync_id",
                    "Deleted Document-gcalendar_sync_id",
                    "Event-gcalendar_sync_id",
                    "Stock Entry Detail-ashbee_attribute_type",
                    "Stock Entry Detail-ashbee__sec_attr",
                    "Timesheet-ashbee_ot2",
                    "Timesheet-ashbee_col_1",
                    "Timesheet-ashbee_ot1",
                    "Project-ashbee_job_detail",
                    "Project-ashbee_job_col_brk",
                    "Project-ashbee_job_intercharge",
                    "Project-ashbee_project_job",
                    "Project-ashbee_salesman",
                    "Project-ashbee_project_code",
                    "Project-ashbee_total_direct_cost",
                    "Stock Entry-ashbee_issue_items",
                    "Item-ashbee_weight",
                    "Item-ashbee_bar",
                    "Stock Entry-ashbee_supplier",
                    "Material Request Item-section_break_5",
                    "Material Request Item-ashbee_finished_item"
                    "Material Request Item-ashbee_finished_item_valuation",
                    "Material Request Item-ashbee_create_variant",
                    "Material Request Item-column_break_7",
                    "Project-ashbee_total_indirect_cost",
                    "Stock Entry-ashbee_production_issue",
                    "Project-ashbee_total_central_cost",
                    "Stock Entry-ashbee_is_return",
                    "Project-ashbee_total_central_labor",
                    "Project-ashbee_total_material_return",
                    "Project-ashbee_total_overhead_charges",
                    "Project-ashbee_location",
                    "Project-ashbee_quotation_ref_no",
                    "Project-ashbee_color",
                    "Project-ashbee_variation",
                    "Project-ashbee_variations",
                    "Project-ashbee_total_variation",
                    "Material Request-ashbee_warehouse"
                ]
            ]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Stock Entry-naming_series-options",
                    "Purchase Receipt-naming_series-options",
                    "Material Request-naming_series-options",
                    "Stock Entry-purpose-options",
                    "Material Request-material_request_type-default"
                ]
            ]
        ]
    }
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "ashbee.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ashbee.install.before_install"
# after_install = "ashbee.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ashbee.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item": {
        "validate": "ashbee.ashbee.customs.items.item_save"
    },
    "Timesheet": {
        "validate": "ashbee.ashbee.customs.timesheet.timesheet_save",
        "on_submit": "ashbee.ashbee.customs.timesheet.timesheet_submit",
        "on_cancel": "ashbee.ashbee.customs.timesheet.timesheet_cancel"
    },
    "Stock Entry": {
        "validate": "ashbee.ashbee.customs.stock_entry.stock_entry_save",
        "on_submit": "ashbee.ashbee.customs.stock_entry.stock_entry_submit",
        "on_cancel": "ashbee.ashbee.customs.stock_entry.stock_entry_cancel"
    },
    "Project": {
        "validate": "ashbee.ashbee.customs.project.project_save"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ashbee.tasks.all"
# 	],
# 	"daily": [
# 		"ashbee.tasks.daily"
# 	],
# 	"hourly": [
# 		"ashbee.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ashbee.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ashbee.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "ashbee.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ashbee.event.get_events"
# }

