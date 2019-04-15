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
# app_include_css = "/assets/ashbee/css/ashbee.css"
# app_include_js = "/assets/ashbee/js/ashbee.js"

# include js, css files in header of web template
# web_include_css = "/assets/ashbee/css/ashbee.css"
# web_include_js = "/assets/ashbee/js/ashbee.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
				"Stock Entry" : "public/js/stock_entry.js",
				"Timesheet" : "public/js/timesheet.js"
			}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

fixtures=["Custom Field"]

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
	"Item":{
		"validate":"ashbee.ashbee.customs.items.item_save"
	},
	"Timesheet":{
		"validate":"ashbee.ashbee.customs.timesheet.timesheet_save"
	}
	# "Stock Entry":{
	# 	"validate":"ashbee.ashbee.customs.stock_entry.stock_entry_validate"
	# }

	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
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

