import json
import frappe


# def before_save(doc, method):
#     if doc.get("stock_entry_type") == "Harvesting of Fish":
        
#         hcf, l_warehouse, hcf_item= frappe.db.get_value("HCF Item",{"period": "Oct 2024", "company": doc.company},["hcf", "lake_warehouse_name", "hcf_item"])

#         if doc.items:
#             for item in doc.items:
#                 if item.t_warehouse:
#                     doc.append("items",{
#                         "item_code": hcf_item,
#                         "s_warehouse": l_warehouse,
#                         "custom_fcr": hcf,
#                         "qty": item.qty*hcf
#                     })
        # doc.save()
@frappe.whitelist()
def add_hcf():
    data_list = []
    
    data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
    doc = data.get("doc")
    
    if doc.get("stock_entry_type") == "Harvesting of Fish":
        hcf, l_warehouse, hcf_item= frappe.db.get_value("HCF Item",{"period": "Oct 2024", "company": doc.get("company")},["hcf", "lake_warehouse_name", "hcf_item"])
    
        item_to_append ={
            "item_code": hcf_item,
            "s_warehouse": l_warehouse,
            "custom_hcf": hcf
            # "qty": item.qty*hcf
        }
        
        data_list.append(item_to_append)
        
        frappe.response['message'] = data_list