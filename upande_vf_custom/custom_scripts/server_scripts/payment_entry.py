import json
import frappe

def before_insert(doc, method):
    po_list = []
    
    if doc.payment_type=="Pay" and len(doc.references):
        ref = doc.references[0]
        
        if ref.reference_doctype=="Purchase Invoice" and ref.reference_name:
            p_items = frappe.db.get_all("Purchase Invoice Item", filters={"parent": ref.reference_name}, fields=["purchase_order"])
            
            for item in p_items:
                if not item.purchase_order in po_list:
                    po_list.append(item.purchase_order)
                    
            if len(po_list)==1:
                pe_ref = po_list[0]
            
                if pe_ref:
                    doc.reference_no = pe_ref
                else:
                    return
                
        
def before_save(doc,method):
    outstanding_bal = 0
    withh_tax = 0
    
    if len(doc.get("references")):
        for item in doc.get("references"):
            if item.get("reference_doctype")=="Purchase Invoice" and item.get("reference_name"):
                tax_deducted = frappe.db.get_value("Purchase Invoice", item.get("reference_name"), "taxes_and_charges_deducted")
                withh_tax += tax_deducted
                
            outstanding_amount = float(item.get("total_amount") - item.get("allocated_amount"))
            
            if outstanding_amount > 0:
                outstanding_bal = outstanding_bal+outstanding_amount
            
        doc.custom_total_outstanding_amount = outstanding_bal   
        doc.custom_withholding_taxes = withh_tax     
    
@frappe.whitelist()  
def get_supplier_details():
    response = {}

    data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
    party = data.get("party")
    
    contact_link = frappe.db.get_value('Dynamic Link', {'link_doctype': 'Supplier', "link_name": party, "parenttype": "Contact"}, 'parent')
    
    if contact_link:
        email = frappe.db.get_value('Contact', {'name': contact_link}, 'email_id')
        
        response["contact"] = contact_link
        response["email"] = email
        
    bank_acc = frappe.db.get_value('Bank Account', {'party_type': 'Supplier', "party": party, "is_default": 1, "is_company_account": 0}, 'name')
    
    if bank_acc:
        response["bank_acc"] = bank_acc

    return response
    
@frappe.whitelist()
def get_reference_no():
    po_list = []
    pe_ref = ""
    
    if frappe.form_dict.message:
        data = json.loads(frappe.form_dict.message)
        doc = data.get("doc")
        
        if doc.get("payment_type")=="Pay" and doc.get("references"):
            # frappe.msgprint("Hello")
            if not doc.get("reference_no"):
                ref = doc.get("references")[0]
                
                if ref.get("reference_doctype")=="Purchase Invoice" and ref.get("reference_name"):
                    p_items = frappe.db.get_all("Purchase Invoice Item", filters={"parent": ref.get("reference_name")}, fields=["purchase_order"])
                    
                    for item in p_items:
                        if not item.get("purchase_order") in po_list:
                            po_list.append(item.get("purchase_order"))
                            
                if len(po_list)==1:
                    pe_ref = po_list[0]
                    
                
        frappe.response['message'] = pe_ref
            