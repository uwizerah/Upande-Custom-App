app_name = "upande_vf_custom"
app_title = "Upande Vf Custom"
app_publisher = "Upande Ltd"
app_description = "Upande Customizations app for Victory Farms"
app_email = "dev@upande.com"
app_license = "mit"





# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/upande_vf_custom/css/upande_vf_custom.css"
# app_include_js = "/assets/upande_vf_custom/js/upande_vf_custom.js"

# include js, css files in header of web template
# web_include_css = "/assets/upande_vf_custom/css/upande_vf_custom.css"
# web_include_js = "/assets/upande_vf_custom/js/upande_vf_custom.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "upande_vf_custom/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page

# include js in page
page_js = {
    "page": "public/js/file.js"
}

doctype_js = {
    "Asset": "custom_asset_scripts/asset.js",
    "Project": "custom_asset_scripts/project.js",
    "Payment Entry": "custom_scripts/client_scripts/payment_entry.js",
    # "Purchase Invoice": "custom_scripts/client_scripts/purchase_invoice.js",
    "Purchase Receipt": "custom_scripts/client_scripts/purchase_receipt.js",
	"Sales Order": "custom_scripts/client_scripts/sales_order.js",
	"Stock Entry": "custom_scripts/client_scripts/stock_entry.js"
}


# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "upande_vf_custom/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "upande_vf_custom.utils.jinja_methods",
#	"filters": "upande_vf_custom.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "upande_vf_custom.install.before_install"
# after_install = "upande_vf_custom.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "upande_vf_custom.uninstall.before_uninstall"
# after_uninstall = "upande_vf_custom.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "upande_vf_custom.utils.before_app_install"
# after_app_install = "upande_vf_custom.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "upande_vf_custom.utils.before_app_uninstall"
# after_app_uninstall = "upande_vf_custom.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "upande_vf_custom.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
		"Asset Value Adjustment": "upande_vf_custom.custom_asset_scripts.custom_asset_value_adjustment.CustomAssetValueAdjustment"

}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {

    "Asset Movement": {
        "after_save": "upande_vf_custom.custom_asset_scripts.asset_movement.after_save",
        "before_submit": "upande_vf_custom.custom_asset_scripts.asset_movement.before_submit"
    },

	"Payment Entry": {
		"before_insert": "upande_vf_custom.custom_scripts.server_scripts.payment_entry.before_insert",
		"before_save": "upande_vf_custom.custom_scripts.server_scripts.payment_entry.before_save"
	},
 	"Sales Order": {
		"on_submit": "upande_vf_custom.custom_scripts.server_scripts.sales_order.on_submit",
  		"before_save": "upande_vf_custom.custom_scripts.server_scripts.sales_order.before_save"
	},
 	"Delivery Note": {
		"on_submit": "upande_vf_custom.custom_scripts.server_scripts.delivery_note.on_submit",
		# "before_save": "upande_vf_custom.custom_scripts.server_scripts.delivery_note.on_save"
	},
	# "Journal Entry": {
	# 	"on_submit": "upande_vf_custom.custom_scripts.server_scripts.journal_entry.on_submit"
	# },
  	"Stock Entry": {
  		"after_insert": "upande_vf_custom.custom_scripts.server_scripts.stock_entry.after_insert"
	},
	"Purchase Invoice": {
		"on_submit": "upande_vf_custom.custom_scripts.server_scripts.purchase_invoice.on_submit",
	}
	
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron":{
		"50 23 * * *": [
			"upande_vf_custom.upande_vf_custom.doctype.mpesa_consolidation.mpesa_consolidation.auto_create_mpesa_to_cons_sweep_journal"
		],
		"20 0 * * *": [
			"upande_vf_custom.upande_vf_custom.doctype.mpesa_to_bank_sweep.mpesa_to_bank_sweep.auto_create_mpesa_to_bank_sweep_journal"
		]
	}
	# "daily": [
	# 	"upande_vf_custom.tasks.daily"
	# ],
#	"hourly": [
#		"upande_vf_custom.tasks.hourly"
#	],
#	"weekly": [
#		"upande_vf_custom.tasks.weekly"
#	],
#	"monthly": [
#		"upande_vf_custom.tasks.monthly"
#	],
}

# Testing
# -------

# before_tests = "upande_vf_custom.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "upande_vf_custom.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "upande_vf_custom.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["upande_vf_custom.utils.before_request"]
# after_request = ["upande_vf_custom.utils.after_request"]

# Job Events
# ----------
# before_job = ["upande_vf_custom.utils.before_job"]
# after_job = ["upande_vf_custom.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"upande_vf_custom.auth.validate"
# ]
get_matching_queries = (
	"upande_vf_custom.upande_vf_custom.doctype.vf_bank_reconciliation_tool.vf_bank_reconciliation_tool.get_matching_queries"
)
get_amounts_not_reflected_in_system_for_vf_bank_reconciliation_statement = "upande_vf_custom.upande_vf_custom.report.vf_bank_reconciliation_statement.vf_bank_reconciliation_statement.get_amounts_not_reflected_in_system_for_vf_bank_reconciliation_statement"
get_entries_for_vf_bank_reconciliation_statement = "upande_vf_custom.upande_vf_custom.report.vf_bank_reconciliation_statement.vf_bank_reconciliation_statement.get_entries_for_vf_bank_reconciliation_statement"
