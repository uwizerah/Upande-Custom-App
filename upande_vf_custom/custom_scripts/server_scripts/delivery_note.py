import frappe

def on_submit(doc, method):
    create_sales_invoice(doc)

def create_sales_invoice(doc):
    if doc.set_warehouse:
        new_stck_entry = frappe.new_doc("Sales Invoice")
        new_stck_entry.company = doc.get("company")
        new_stck_entry.customer = doc.get("customer")
        new_stck_entry.cost_center = doc.get("cost_center")
        
        for item in doc.items:
            new_stck_entry.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "item_name":item.get("item_name"),
                "description":item.get("description"),
                "cost_center": item.get("cost_center"),
                "sales_order": item.get("against_sales_order"),
                "so_detail": item.get("so_detail"),
                "delivery_note": doc.get("name")
            })
            
        new_stck_entry.save()
        
        new_stck_entry.submit()
        
    else:
        frappe.throw("Check Delivery Note Info!")