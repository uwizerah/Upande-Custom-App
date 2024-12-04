import frappe
from frappe import _

def on_submit(doc, method):
    # Check if there are any attachments linked to the document
    attachments = frappe.get_all('File', filters={'attached_to_doctype': doc.doctype, 'attached_to_name': doc.name})
    
    if not attachments:
        frappe.throw(_("Please Attach a Reference Document."))

    if doc.set_warehouse and doc.custom_driver_consignment_note_number:
        create_sales_invoice(doc)
        
        variance_list =  variance_due_to_water_loss(doc)
        
        move_variance_to_wh(doc.custom_driver_consignment_note_number, doc.custom_variance_warehouse, doc.set_warehouse, doc.company, doc.cost_center, variance_list)
        
def create_sales_invoice(doc):
    new_sinv = frappe.new_doc("Sales Invoice")
    new_sinv.company = doc.get("company")
    new_sinv.customer = doc.get("customer")
    new_sinv.custom_is_credit_sale = 1
    new_sinv.selling_price_list = doc.selling_price_list
    new_sinv.set_posting_time = 1
    new_sinv.posting_date = doc.posting_date
    new_sinv.pos_profile = doc.get("pos_profile")
    new_sinv.cost_center = doc.get("cost_center")
    
    for item in doc.items:
        new_sinv.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "item_name":item.get("item_name"),
            "pos_profile": doc.get("pos_profile"),
            "description":item.get("description"),
            "cost_center": item.get("cost_center"),
            "sales_order": item.get("against_sales_order"),
            "so_detail": item.get("so_detail"),
            "delivery_note": doc.get("name")
        })
        
    new_sinv.save()
    
    new_sinv.submit()
        
def get_dn_items(doc):
    dn_items = []
    if doc.custom_driver_consignment_note_number:
        for item in doc.items:
            item_dict = {
                "item_code": item.get("item_code"),
                "uom": item.get("uom"),
                "qty": item.get("qty")
            }
            
            if not item_dict in dn_items:
                dn_items.append(item_dict)
    
    return dn_items

def get_stock_entries(doc):
    se_names = []
    stck_entries = frappe.db.get_all("Stock Entry", filters={"custom_consignment_note": doc.custom_driver_consignment_note_number, "docstatus": 1}, fields=["name"])
    
    if stck_entries:
        for entry in stck_entries:
            if not entry.get("name") in se_names:
                se_names.append(entry.get("name"))
                
    return se_names
                
def variance_due_to_water_loss(doc):
    se_names = get_stock_entries(doc)
    dn_items = get_dn_items(doc)
    variance_list = []
    
    stck_items = frappe.db.get_all("Stock Entry Detail", filters={"parent": ['in', se_names]}, fields=["item_code", "qty", "uom"])
    
    for item in dn_items:
        for stck in stck_items:
            if item.get("item_code") == stck.get("item_code"):
                if item.get("uom") == stck.get("uom"):
                    variance = {
                        "item_code": item.get("item_code"),
                        "uom": item.get("uom"),
                        "variance": float(stck.get("qty")) - float(item.get("qty"))
                    }
                    if float(stck.get("qty")) - float(item.get("qty")):
                        if not variance in variance_list:
                            variance_list.append(variance)

    return variance_list
                        
def move_variance_to_wh(c_no, variance_warehouse, s_warehouse, company, cost_center, variance_list):
    if len(variance_list):
        new_stk_entry = frappe.new_doc("Stock Entry")
        new_stk_entry.company = company
        new_stk_entry.cost_center = cost_center
        new_stk_entry.custom_consignment_note = c_no
        new_stk_entry.from_warehouse = s_warehouse
        new_stk_entry.to_warehouse = variance_warehouse
        
        for item in variance_list:
            if float(item.get("variance")) > 0:
                new_stk_entry.append("items",{
                    "item_code": item.get("item_code"),
                    "qty": item.get("variance"),
                    "uom": item.get("uom")
                })
            
        new_stk_entry.save()
        new_stk_entry.submit()
                
        

        
        