# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document


class BulkUpload(Document):
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
        self.items = []

        draft_payments = frappe.db.get_all('Payment Entry', filters={
            'status': ['in', ['Draft']],
            'payment_type': 'Pay',
            "custom_upload_type": self.type
        }, fields=['name', 'party', 'paid_amount', 'party_bank_account', 'custom_upload_type'])
        
        if draft_payments:
            for pymnt in draft_payments:
                if pymnt.get("custom_upload_type") in ["EFT", "RTGS", "International Payments"]:
                    if pymnt.get("party_bank_account"):
                        
                        bank = frappe.db.get_value("Bank Account", {"name": pymnt.get("party_bank_account")}, 'bank')
                        pymnt["bank_name"] = bank
                        
                        if not pymnt in pymnts_list:
                            pymnts_list.append(pymnt)
                else:
                   if not pymnt in pymnts_list:
                        pymnts_list.append(pymnt) 
                        
        response_data = {
            'draft_payments': pymnts_list
        }
        print("*"*80)
        print(response_data)
        frappe.response['message'] = response_data
        
    @frappe.whitelist()
    def download_report(self):   
        site_url = frappe.utils.get_url()      
        report_url = f"{site_url}/app/query-report/Bank Bulk Upload?parent={self.get('name')}"
        
        frappe.response['message'] = report_url







                        