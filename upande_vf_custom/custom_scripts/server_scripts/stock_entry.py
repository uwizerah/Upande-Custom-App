import json
import frappe

@frappe.whitelist()
def add_hcf():
    data_list = []
    
    data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
    doc = data.get("doc")
    
    # if doc.get("stock_entry_type") == "Harvesting of Fish":
    #     hcf_doc = frappe.db.get_all("Harvest Conversion Factor")
    #     hcf, l_warehouse, hcf_item= frappe.db.get_value("HCF Item",{"period": "Oct 2024", "company": doc.get("company")},["hcf", "lake_warehouse_name", "hcf_item"])
    
    #     item_to_append ={
    #         "item_code": hcf_item,
    #         "s_warehouse": l_warehouse,
    #         "custom_hcf": hcf
    #         # "qty": item.qty*hcf
    #     }
        
    #     data_list.append(item_to_append)
        
    #     frappe.response['message'] = data_list