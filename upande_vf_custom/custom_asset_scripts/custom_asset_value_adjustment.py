# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, formatdate, get_link_to_form, getdate

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_checks_for_pl_and_bs_accounts,
)
from erpnext.assets.doctype.asset.asset import get_asset_value_after_depreciation
from erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule import (
    make_new_active_asset_depr_schedules_and_cancel_current_ones,
)

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
        asset_purchase_date = frappe.db.get_value("Asset", self.asset, "purchase_date")
        if getdate(self.date) < getdate(asset_purchase_date):
            frappe.throw(
                _("Asset Value Adjustment cannot be posted before Asset's purchase date <b>{0}</b>.").format(
                    formatdate(asset_purchase_date)
                ),
                title=_("Incorrect Date"),
            )

    def set_difference_amount(self):
        self.difference_amount = flt(self.current_asset_value - self.new_asset_value)

    def set_current_asset_value(self):
        if not self.current_asset_value and self.asset:
            self.current_asset_value = get_asset_value_after_depreciation(self.asset, self.finance_book)

    def make_depreciation_entry(self):
        asset = frappe.get_doc("Asset", self.asset)
        
        # Fetch fixed asset account and revaluation account from the Asset Category's child table "Asset Category Account"
        accounts = frappe.get_all(
            "Asset Category Account",
            filters={"parent": asset.asset_category}, 
            fields=["fixed_asset_account", "custom_revaluation_account"]
        )
        
        if not accounts:
            frappe.throw(_("No accounts found for Asset Category {0}.").format(asset.asset_category))
        
        
        fixed_asset_account = accounts[0].get("fixed_asset_account")
        revaluation_account = accounts[0].get("custom_revaluation_account")

        # Ensure both accounts were fetched correctly
        if not fixed_asset_account:
            frappe.throw(_("Fixed Asset Account not found in Asset Category {0}.").format(asset.asset_category))

        if not revaluation_account:
            frappe.throw(_("Revaluation Account not found in Asset Category {0}.").format(asset.asset_category))

        depreciation_cost_center, depreciation_series = frappe.get_cached_value(
            "Company", asset.company, ["depreciation_cost_center", "series_for_depreciation_entry"]
        )

        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Depreciation Entry"
        je.naming_series = depreciation_series
        je.posting_date = self.date
        je.company = self.company
        je.remark = f"Depreciation Entry against {self.asset} worth {self.difference_amount}"
        je.finance_book = self.finance_book

        credit_entry = {
            "account": fixed_asset_account,
            "credit_in_account_currency": self.difference_amount,
            "cost_center": depreciation_cost_center or self.cost_center,
            "reference_type": "Asset",
            "reference_name": asset.name,
        }

        debit_entry = {
            "account": revaluation_account,
            "debit_in_account_currency": self.difference_amount,
            "cost_center": depreciation_cost_center or self.cost_center,
            "reference_type": "Asset",
            "reference_name": asset.name,
        }

        accounting_dimensions = get_checks_for_pl_and_bs_accounts()

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

        je.append("accounts", credit_entry)
        je.append("accounts", debit_entry)

        je.flags.ignore_permissions = True
        je.submit()

        self.db_set("journal_entry", je.name)


    def update_asset(self, asset_value):
        asset = frappe.get_doc("Asset", self.asset)

        if not asset.calculate_depreciation:
            asset.value_after_depreciation = asset_value
            asset.save()
            return

        asset.flags.decrease_in_asset_value_due_to_value_adjustment = True

        if self.docstatus == 1:
            notes = _(
                "This schedule was created when Asset {0} was adjusted through Asset Value Adjustment {1}."
            ).format(
                get_link_to_form("Asset", asset.name),
                get_link_to_form(self.get("doctype"), self.get("name")),
            )
        elif self.docstatus == 2:
            notes = _(
                "This schedule was created when Asset {0}'s Asset Value Adjustment {1} was cancelled."
            ).format(
                get_link_to_form("Asset", asset.name),
                get_link_to_form(self.get("doctype"), self.get("name")),
            )

        make_new_active_asset_depr_schedules_and_cancel_current_ones(
            asset, notes, value_after_depreciation=asset_value, ignore_booked_entry=True
        )
        asset.flags.ignore_validate_update_after_submit = True
        asset.save()
