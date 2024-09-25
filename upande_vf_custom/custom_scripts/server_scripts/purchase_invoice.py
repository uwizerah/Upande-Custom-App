import json

import frappe

@frappe.whitelist()
def update_taxes():
    if frappe.form_dict.message:
        data = json.loads(frappe.form_dict.message)
        doc_name = data.get("doc_name")
        doc = frappe.get_doc("Purchase Invoice", doc_name)
        print("*"*80)
        print(doc)
        if doc.get("taxes"):
            for item in doc.get("taxes"):
                if item.get("charge_type") == "On Net Total":
                    print(item.get("included_in_print_rate"))
                    frappe.db.set_value("Purchase Taxes and Charges", item.name, {"included_in_print_rate": 1})
                    print(item.get("included_in_print_rate"))