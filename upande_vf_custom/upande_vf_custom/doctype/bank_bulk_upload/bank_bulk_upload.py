# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
import json

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
    
    @frappe.whitelist()        
    def get_pending_payments(self):
        pymnts_list = []

        draft_payments = frappe.db.get_all('Payment Entry', filters={
            'status': ['in', ['Draft']],
            'payment_type': 'Pay'
        }, fields=['name', 'party_name', 'paid_amount', 'party_bank_account'])
        
        if draft_payments:
            for pymnt in draft_payments:
                if pymnt.get("party_bank_account"):
                    
                    bank_acc = frappe.db.get_value("Bank Account", {"name": pymnt.get("party_bank_account")}, 'bank')
                    pymnt["bank_acc"] = bank_acc
                    
                    if not pymnt in pymnts_list:
                        pymnts_list.append(pymnt)
                        
        response_data = {
            'draft_payments': pymnts_list
        }
        
        frappe.response['message'] = response_data
        
    def report_download(self):
        if frappe.form_dict.message:
            data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
            doc = data.get("record")
           
                    
            report_url = f"https://127.0.0.1:8000/app/query-report/Bank%20Bulk%20Upload2?parent={doc.get('name')}"
            
            frappe.response['message'] = report_url
                
        else:
            frappe.response['message'] = "not ok"







                        