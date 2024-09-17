# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetScrapping(Document):
    def create_journal_entry_for_scrap(self):
        if self.workflow_state == "Scrapped":
            # Fetch the asset
            asset = frappe.get_doc("Asset", self.asset)
            
            # Ensure the asset is submitted and not already scrapped
            if asset.docstatus != 1:
                frappe.throw(f"Asset {asset.name} must be submitted before scrapping.")
            
            if asset.status == "Scrapped":
                frappe.throw(f"Asset {asset.name} is already scrapped.")
            
            # Fixed Asset Account
            fixed_asset_account = frappe.db.get_value("Asset Category Account", {"parent": asset.asset_category}, "fixed_asset_account")
            
            gain_loss_account = "110002 - Profit/Loss On Sale Of Assets - VFL"
            
            # Calculate accumulated depreciation
            accumulated_depreciation = 0
            
            if asset.get("schedules"):
                for item in asset.get("schedules"):
                    # Compare schedule date directly
                    if item.schedule_date <= self.scrap_date:
                        # Accumulate the depreciation amount
                        if item.accumulated_depreciation_amount is not None:
                            accumulated_depreciation = item.accumulated_depreciation_amount
                        else:
                            frappe.throw(f"Accumulated depreciation amount is None for schedule date: {item.schedule_date}")
            
            # Calculate the book value after depreciation
            book_value = asset.gross_purchase_amount - accumulated_depreciation
            
            # Create Journal Entry
            je = frappe.new_doc("Journal Entry")
            je.voucher_type = "Journal Entry"
            je.company = asset.company
            je.posting_date = self.scrap_date
            je.append("accounts", {
                "account": fixed_asset_account,
                "credit_in_account_currency": book_value
            })
            je.append("accounts", {
                "account": gain_loss_account,
                "debit_in_account_currency": book_value
            })
            
            je.insert()
            je.submit()
            
            # Update Asset and Asset Scrapping records
            frappe.db.set_value("Asset", asset.name, "journal_entry_for_scrap", je.name)
            frappe.db.set_value("Asset Scrapping", self.name, "journal_entry_for_scrap", je.name)
            
            # Update Asset status
            frappe.db.set_value("Asset", asset.name, "status", "Scrapped")

    # Call the function to create the journal entry when the status changes to Scrapped
    def on_submit(self):
        self.create_journal_entry_for_scrap()
