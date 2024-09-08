# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BankBulkUpload(Document):
    def before_submit(self):
        if self.items:
            for item in self.items:
                p_entry = frappe.get_doc("Payment Entry", item.payment_reference)
                if p_entry.docstatus==0:
                    p_entry.custom_cash_flow_period = self.cash_flow_period

                    p_entry.save()
                    p_entry.submit()


        