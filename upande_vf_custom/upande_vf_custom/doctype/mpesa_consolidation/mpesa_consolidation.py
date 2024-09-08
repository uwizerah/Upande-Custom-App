# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MpesaConsolidation(Document):
    @frappe.whitelist()
    def get_mpesa_accounts(self):
        result_data = []
        
        if self.get("mpesa_parent"):
            mpesa_accounts = frappe.db.get_all("Account", filters = {"parent_account": self.get("mpesa_parent")}, fields=["name"])

            if mpesa_accounts:
                for account in mpesa_accounts:
                    if self.get("company"):
                        mode_of_payment = frappe.db.get_value('Mode of Payment Account', {
                            'default_account': account.get("name"),
                            "company": self.get("company")
                        }, 'parent')
                        
                        acc_dict = {
                            "from_account": account.get("name"),
                            "to_account": self.get("default_account"),
                            "mode_of_payment": mode_of_payment
                        }
            
                        if not acc_dict in result_data:
                            result_data.append(acc_dict)

                frappe.response['message'] = result_data
            else:
                frappe.response['message'] = "ok"

