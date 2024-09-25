# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document


class DriverConsignmentNote(Document):
    # def before_save(self):
    #     self.validate_crates()
    
    def validate_crates(self):
        items = self.get_items()
        crates = self.get_crates()
        
        for i, q in items.items():
            for c, cq in crates.items():
                if i == c:
                    if not q == cq:
                        frappe.throw("Quantity {} for {} does not match quantity of {} in crates!".format(q,i,cq))
        
        
    def get_items(self):
        items = {}
        if self.items:
            for item in self.items:
                if not item.get("item_code") in items.keys():
                    items[item.get("item_code")] = 0
                items[item.get("item_code")] += item.get("qty")
                
        return items
           
    def get_crates(self):
        crates = {}
        if self.crates:
            for item in self.crates:
                if not item.get("item_code") in crates.keys():
                    crates[item.get("item_code")] = 0
                crates[item.get("item_code")] += item.get("qty")
                
        return crates
         
    @frappe.whitelist()     
    def updated_child_table(self):
        self.crates = []
        self.save()
        
        self.adjust_crates()
            
    def adjust_crates(self):
        items_dict = {}
        if self.items:
            for item in self.items:
                if not item.get("item_code") in items_dict.keys():
                    items_dict[item.get("item_code")] = {}
                
                items_dict[item.get("item_code")] = {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "uom": item.get("uom")
                }
    
        self.convert_to_crates(items_dict)

    def convert_to_crates(self, items_dict):
        for key, value in items_dict.items():
            conv_factor = frappe.db.get_value("UOM Conversion Factor", {"category": "Mass", "from_uom": value.get("uom"), "to_uom": "Crate"}, "value")
            value["crates_qty"] = value["qty"] * conv_factor
    
            value["full_crate_qty"] = value["crates_qty"] // 1
            value["half_crate_qty"] = value["crates_qty"] % 1

        # List to store the new entries
        crate_list = []

        # Initialize a global crate number
        global_crate_number = 1

        # Loop through each item in the dictionary
        for item_name, details in items_dict.items():
            total_qty = details['qty']
            full_crates = int(total_qty // 25)  # Calculate full crates (25 kgs per crate)
            remaining_qty = total_qty % 25  # Calculate remaining quantity for half crate

            # Create entries for each full crate
            for i in range(full_crates):
                crate_entry = {
                    'item_code': details['item_code'],
                    'crate_number': global_crate_number,
                    'uom': details['uom'],
                    'qty': 25,  # Each full crate holds 25 kgs
                    'crate_type': 'Full Crate'
                }
                crate_list.append(crate_entry)
                global_crate_number += 1  # Increment the global crate number

            # If there is remaining quantity (half crate), add that as well
            if remaining_qty > 0:
                crate_entry = {
                    'item_code': details['item_code'],
                    'crate_number': global_crate_number,
                    'uom': details['uom'],
                    'qty': remaining_qty,  # Remaining quantity for half crate
                    'crate_type': 'Half Crate'
                }
                crate_list.append(crate_entry)
                global_crate_number += 1  # Increment the global crate number

        self.append_crates(crate_list)
        
    def append_crates(self, crate_list):
        for crate in crate_list:
            # Check if the crate already exists
            existing_crate = next((c for c in self.crates if c.item_code == crate['item_code'] and c.crate_number == crate['crate_number']), None)

            if existing_crate:
                # If the crate exists, update the quantity
                existing_crate.qty = crate['qty']
            else:
                # If the crate does not exist, create a new entry
                self.append("crates", {
                    'item_code': crate['item_code'],
                    'crate_number': crate['crate_number'],
                    'uom': crate['uom'],
                    'qty': crate['qty'],
                    # 'crate_type': crate['crate_type']
                })
            self.save()

                    
    def on_submit(self):
        if not self.crates:
            frappe.throw("Crates table is mandatory!")
            
        self.validate_crates()
            
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
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "cost_center": item.get("cost_center"),
                    "vf_crate_no": item.get("idx")
                })
                
            new_stck_entry.save()
            new_stck_entry.submit()
            
            self.stock_transfer_number = new_stck_entry.name
        else:
            frappe.throw("Check Consignment Note Info!")
    

    @frappe.whitelist()
    def create_delivery_note(self):  
        if self.get("docstatus")==1:
            dn_exists = frappe.db.exists("Delivery Note", {"custom_driver_consignment_note_number": self.name})

            if not dn_exists:
                new_stck_entry = frappe.new_doc("Delivery Note")
                new_stck_entry.company = self.get("company")
                new_stck_entry.set_warehouse = self.get("truck_warehouse")
                new_stck_entry.customer = self.get("customer")
                new_stck_entry.customer_name = self.get("customer_name")
                new_stck_entry.cost_center = self.get("cost_center")
                new_stck_entry.driver = self.get("driver")
                new_stck_entry.vehicle_no = self.get("vehicle")
                new_stck_entry.custom_driver_consignment_note_number = self.name
                
                for item in self.get("items"):
                    new_stck_entry.append("items", {
                        "item_code": item.get("item_code"),
                        "qty": item.get("qty"),
                        "description":item.get("description"),
                        "item_name":item.get("item_name"),
                        "uom":item.get("uom"),
                        "delivery_date": item.get("delivery_date"),
                        "cost_center": item.get("cost_center"),
                        "rate": item.get("rate"),
                        "against_sales_order": self.get("sales_order_number"),
                        "so_detail": item.get("so_detail"),
                        "amount": item.get("amount"),
                    })
                    
                new_stck_entry.save()
                
                self.delivered = 1
                self.save()
                
                frappe.response['message'] = new_stck_entry    
            else:
                frappe.throw("Delivery Note {} exists for {}".format(dn_exists, self.name))
        else:
            frappe.throw("Delivery Note Must Be Submitted!")