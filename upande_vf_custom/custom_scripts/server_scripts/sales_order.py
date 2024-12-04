import json

import frappe

def before_save(doc, method):
    if not doc.customer_address:
        frappe.msgprint("Customer address is missing, provide it to System Admin to enable smooth delivery.")
    
def on_submit(doc, method):
    create_consignment_note(doc)

def create_consignment_note(doc):
    if doc.set_warehouse:
        create_so_onsubmit(doc)
         
def create_so_onsubmit(doc):
    new_dcn = frappe.new_doc("Driver Consignment Note")
    new_dcn.company = doc.company
    new_dcn.customer = doc.customer
    new_dcn.customer_name = doc.customer_name
    new_dcn.customer_address = doc.customer_address
    new_dcn.from_warehouse = doc.set_warehouse
    new_dcn.selling_price_list = doc.selling_price_list
    new_dcn.pos_profile = doc.pos_profile
    new_dcn.cost_center = doc.cost_center
    new_dcn.delivery_date = doc.delivery_date
    new_dcn.sales_order_number = doc.name
    new_dcn.lc_manager = doc.custom_lc_manager
    new_dcn.variance_warehouse = doc.custom_variance_warehouse
    
    for item in doc.items:
        new_dcn.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "item_name":item.item_name,
            "description":item.description,
            "cost_center": doc.get("cost_center"),
            "uom":item.uom,
            "delivery_date": item.delivery_date,
            "rate": item.rate,
            "so_detail": item.name,
            "amount": item.amount,
        })
        
    new_dcn.save()
    frappe.db.commit()
        
@frappe.whitelist()
def create_so():
    data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
    doc_name = data.get("doc_name")
    doc = frappe.db.get("Sales Order", doc_name)
    
    # dcn_exists = frappe.db.exists()

    
    new_so = frappe.new_doc("Driver Consignment Note")
    new_so.company = doc.company
    new_so.customer = doc.customer
    new_so.customer_name = doc.customer_name
    new_so.customer_address = doc.customer_address
    new_so.from_warehouse = doc.set_warehouse
    new_so.cost_center = doc.cost_center
    new_so.delivery_date = doc.delivery_date
    new_so.sales_order_number = doc.name
    new_so.lc_manager = doc.custom_lc_manager
    
    for item in doc.items:
        new_so.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "item_name":item.item_name,
            "description":item.description,
            "cost_center": doc.get("cost_center"),
            "uom":item.uom,
            "delivery_date": item.delivery_date,
            "rate": item.rate,
            "so_detail": item.name,
            "amount": item.amount,
        })
        
    new_so.save()    
    frappe.db.commit()

