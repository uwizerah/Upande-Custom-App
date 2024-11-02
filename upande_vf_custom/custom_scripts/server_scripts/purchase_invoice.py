import json

import frappe
from frappe import _

def on_submit(doc, method):
    # Check if there are any attachments linked to the document
    attachments = frappe.get_all('File', filters={'attached_to_doctype': doc.doctype, 'attached_to_name': doc.name})
    
    if not attachments:
        frappe.throw(_("Please Attach a Reference Document."))
        
# @frappe.whitelist()
# def update_taxes():
#     if frappe.form_dict.message:
#         data = json.loads(frappe.form_dict.message)
#         doc_name = data.get("doc_name")
#         doc = frappe.get_doc("Purchase Invoice", doc_name)
#         if doc.get("taxes"):
#             for item in doc.get("taxes"):
#                 if item.get("charge_type") == "On Net Total":
#                     item.included_in_print_rate = 1
                    
#             doc.save()
            
#     assign_expense_account(doc)
    
            
# def assign_expense_account(doc):
#     taxes_dict = {}
#     items_info = get_tax_accounts(doc)
    
#     for item in items_info:
#         if not item.get("account") in taxes_dict.keys():
#             taxes_dict[item.get("account")] = 0
            
#         taxes_dict[item.get("account")] += item.get("tax_amount")
    
#     append_taxes(doc, taxes_dict)

# def append_taxes(doc, taxes_dict):
#     for item in doc.items:
#         print("*"*80)
#         print(item.__dict__)
#     # if taxes_dict:
        
#     #     # for key, value in taxes_dict.items():
#     #     #     doc.append("taxes", {
#     #     #         "category": "Total",
#     #     #         "add_deduct_tax": "Add",
#     #     #         "charge_type": "On Net Total",
#     #     #         "account_head": key,
#     #     #         "description": "Hee",
#     #     #         "tax_amount": value
#     #     #     })
#     #     # doc.save()
#     #     print("*"*80)
#     #     print(doc.__dict__)
        
# def get_tax_accounts(doc):
#     info_list = []
#     if doc.items:
#         for item in doc.get("items"):
#             if item.get("item_tax_template") and item.get("net_rate"):
#                 item_info = {
#                     "account": item.get("expense_account"),
#                     "rate": item.get("rate"),
#                     "tax_amount": item.get("rate") - item.get("net_rate")
#                 }

#                 if not item_info in info_list:
#                     info_list.append(item_info)
                    
#     return info_list