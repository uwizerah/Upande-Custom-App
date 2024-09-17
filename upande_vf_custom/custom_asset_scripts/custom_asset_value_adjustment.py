import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, formatdate, getdate
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_checks_for_pl_and_bs_accounts,
)
from erpnext.assets.doctype.asset.asset import get_asset_value_after_depreciation
from erpnext.assets.doctype.asset.depreciation import get_depreciation_accounts


class CustomAssetValueAdjustment(Document):
	def validate(self):
		self.validate_date()
		self.set_current_asset_value()
		self.set_difference_amount()

	def on_submit(self):
		self.make_depreciation_entry()
		self.update_asset(self.new_asset_value)

	def on_cancel(self):
		self.update_asset(self.current_asset_value)

	def validate_date(self):
		# Fetch the asset purchase date to validate the adjustment date
		asset_purchase_date = frappe.db.get_value("Asset", self.asset, "purchase_date")
		if getdate(self.date) < getdate(asset_purchase_date):
			frappe.throw(
				_("Asset Value Adjustment cannot be posted before the Asset's purchase date <b>{0}</b>.").format(
					formatdate(asset_purchase_date)
				),
				title=_("Incorrect Date"),
			)

	def set_difference_amount(self):
		# Calculate the difference between the current and new asset values
		self.difference_amount = flt(self.current_asset_value - self.new_asset_value)

	def set_current_asset_value(self):
		# Set the current asset value if not already set
		if not self.current_asset_value and self.asset:
			self.current_asset_value = get_asset_value_after_depreciation(self.asset, self.finance_book)

	def make_depreciation_entry(self):
		# Get the asset document
		asset = frappe.get_doc("Asset", self.asset)

		# Fetch the accounts from the asset category child table
		fixed_asset_account, custom_revaluation_account = frappe.db.get_value(
			"Asset Category Account", 
			{"parent": asset.asset_category, "company_name": asset.company}, 
			["fixed_asset_account", "custom_revaluation_account"]
		)

		# Ensure accounts exist
		if not fixed_asset_account or not custom_revaluation_account:
			frappe.throw(_("Please ensure that both Fixed Asset Account and Custom Revaluation Account are set in the Asset Category for {0}.").format(asset.asset_category))

		# Fetch depreciation cost center and series from company settings
		depreciation_cost_center, depreciation_series = frappe.get_cached_value(
			"Company", asset.company, ["depreciation_cost_center", "series_for_depreciation_entry"]
		)

		# Create a new Journal Entry document
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Depreciation Entry"
		je.naming_series = depreciation_series
		je.posting_date = self.date
		je.company = self.company
		je.remark = f"Depreciation Entry against {self.asset} worth {self.difference_amount}"
		je.finance_book = self.finance_book

		# Create credit entry for Fixed Asset Account and debit entry for Custom Revaluation Account
		credit_entry = {
			"account": fixed_asset_account,
			"credit_in_account_currency": self.difference_amount,
			"cost_center": depreciation_cost_center or self.cost_center,
			"reference_type": "Asset",
			"reference_name": asset.name,
		}

		debit_entry = {
			"account": custom_revaluation_account,
			"debit_in_account_currency": self.difference_amount,
			"cost_center": depreciation_cost_center or self.cost_center,
			"reference_type": "Asset",
			"reference_name": asset.name,
		}

		# Fetch any accounting dimensions that need to be applied
		accounting_dimensions = get_checks_for_pl_and_bs_accounts()

		# Update accounting dimension data for both credit and debit entries
		for dimension in accounting_dimensions:
			if dimension.get("mandatory_for_bs"):
				credit_entry.update(
					{
						dimension["fieldname"]: self.get(dimension["fieldname"])
						or dimension.get("default_dimension")
					}
				)

			if dimension.get("mandatory_for_pl"):
				debit_entry.update(
					{
						dimension["fieldname"]: self.get(dimension["fieldname"])
						or dimension.get("default_dimension")
					}
				)

		# Append the entries to the Journal Entry document
		je.append("accounts", credit_entry)
		je.append("accounts", debit_entry)

		# Submit the Journal Entry
		je.flags.ignore_permissions = True
		je.submit()

		# Set the Journal Entry name in the Asset Value Adjustment document
		self.db_set("journal_entry", je.name)

	def update_asset(self, asset_value):
		# Fetch the asset document
		asset = frappe.get_doc("Asset", self.asset)

		# Set the flag indicating a decrease in asset value due to value adjustment
		asset.flags.decrease_in_asset_value_due_to_value_adjustment = True

		# Prepare the asset for depreciation after the value adjustment
		asset.prepare_depreciation_data(value_after_depreciation=asset_value, ignore_booked_entry=True)
		asset.flags.ignore_validate_update_after_submit = True
		asset.save()
