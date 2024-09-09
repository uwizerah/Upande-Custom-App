# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document


class DriverConsignmentNote(Document):
    def before_submit(self):
        if self.from_warehouse and self.sales_order_number:
            new_stck_entry = frappe.new_doc("Stock Entry")
            new_stck_entry.company = self.company
            new_stck_entry.from_warehouse = self.from_warehouse
            new_stck_entry.to_warehouse = self.truck_warehouse
            new_stck_entry.add_to_transit = 1
            new_stck_entry.driver = self.driver
            new_stck_entry.purpose = "Material Transfer"
            new_stck_entry.destination_warehouse = self.truck_warehouse
            new_stck_entry.custom_consignment_note = self.name
            
            for item in self.items:
                new_stck_entry.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "vf_crate_no": item.idx
                })
                
            new_stck_entry.save()
            new_stck_entry.submit()
            
            self.stock_transfer_number = new_stck_entry.name
        else:
            frappe.throw("Check Consignment Note Info!")
    

    @frappe.whitelist()
    def create_delivery_note(self):
        if self.get("docstatus")==1:
            new_stck_entry = frappe.new_doc("Delivery Note")
            new_stck_entry.company = self.get("company")
            new_stck_entry.set_warehouse = self.get("truck_warehouse")
            new_stck_entry.customer = self.get("customer")
            new_stck_entry.customer_name = self.get("customer_name")
            new_stck_entry.cost_center = self.get("cost_center")
            new_stck_entry.driver = self.get("driver")
            new_stck_entry.vehicle_no = self.get("vehicle")
            # new_stck_entry.custom_consignment_note = self.name
            
            for item in self.get("items"):
                new_stck_entry.append("items", {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "description":item.get("description"),
                    "item_name":item.get("item_name"),
                    "uom":item.get("uom"),
                    "delivery_date": item.get("delivery_date"),
                    "rate": item.get("rate"),
                    "against_sales_order": self.get("sales_order_number"),
                    "so_detail": item.get("so_detail"),
                    "amount": item.get("amount"),
                })
                
            new_stck_entry.save()
            #     # new_stck_entry.submit()
            frappe.response['message'] = new_stck_entry
            # frappe.response['message'] = "new_stck_entry"
        else:
            frappe.throw("Missing Arguments!")
            
        
