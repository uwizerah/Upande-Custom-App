import json

import frappe

@frappe.whitelist()
def create_landed_cost_voucher():
    if frappe.form_dict.message:
        data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
        r_name = data.get("r_name")
        
        purchase_receipt = frappe.get_doc("Purchase Receipt", r_name)
        
        # Check if the custom_type is 'Feeds'
        if purchase_receipt.get("custom_type") != "Feeds":
            frappe.throw("Landed Cost Voucher can only be created for Purchase Receipts with custom type 'Feeds'.")
        
            
        l_costs = frappe.get_doc("Landed Costs", "2024")
        
        # Create a new Landed Cost Voucher document
        new_lcv = frappe.new_doc("Landed Cost Voucher")
        new_lcv.company = purchase_receipt.get("company")
        new_lcv.posting_date = purchase_receipt.get("posting_date")
    
        # Append to 'purchase_receipts' table within Landed Cost Voucher
        new_lcv.append("purchase_receipts", {
            "receipt_document_type": "Purchase Receipt",
            "receipt_document": purchase_receipt.get("name"),
            "supplier": purchase_receipt.get("supplier"),
            "grand_total": purchase_receipt.get("grand_total")
        })

        # Append items from Purchase Receipt to LCV
        for item in purchase_receipt.get("items"):
            new_lcv.append("items", {
                "item_code": item.get("item_code"),
                "description": item.get("description"),
                "receipt_document_type": "Purchase Receipt",
                "receipt_document": purchase_receipt.get("name"),
                "cost_center": item.get("cost_center"),
                "qty": item.get("received_qty"),
                "uom": item.get("uom"),
                "rate": item.get("net_rate"),
                "amount": item.get("net_amount")
            })
        
        
        if l_costs:
            for itm in l_costs.get("items"):
                new_lcv.append("taxes", {
                    "expense_account": itm.get("expense_account"),
                    "account_currency": itm.get("account_currency"),
                    "description": itm.get("description"),
                    "amount": itm.get("amount")
                })

        # Insert and submit the Landed Cost Voucher
        new_lcv.save()
        new_lcv.submit()
    
        frappe.response['message'] = new_lcv.name