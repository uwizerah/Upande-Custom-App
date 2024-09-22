import frappe

def before_save(doc, method):
    if not doc.customer_address:
        frappe.msgprint("Customer address is missing, provide it to System Admin to enable smooth delivery.")
    
def on_submit(doc, method):
    create_consignment_note(doc)

def create_consignment_note(doc):
    if doc.set_warehouse:
        new_stck_entry = frappe.new_doc("Driver Consignment Note")
        new_stck_entry.company = doc.company
        new_stck_entry.customer = doc.customer
        new_stck_entry.customer_name = doc.customer_name
        new_stck_entry.customer_address = doc.customer_address
        new_stck_entry.from_warehouse = doc.set_warehouse
        new_stck_entry.cost_center = doc.cost_center
        new_stck_entry.delivery_date = doc.delivery_date
        new_stck_entry.sales_order_number = doc.name
        new_stck_entry.lc_manager = doc.custom_lc_manager
        
        for item in doc.items:
            new_stck_entry.append("items", {
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
            
        new_stck_entry.save()
        # doc.custom_consignment_number = new_stck_entry.name
        
        new_stck_entry.save()
        
    else:
        frappe.throw("Check Sales Order Info!")