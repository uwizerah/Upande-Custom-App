import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.meta import get_field_precision
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import flt

import erpnext
from erpnext.controllers.taxes_and_totals import init_landed_taxes_and_totals
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos


@frappe.whitelist()
def create_landed_cost_voucher():
    if frappe.form_dict.message:
        data = json.loads(frappe.form_dict.message) # Parsing JSON to a dictionary
        r_name = data.get("r_name")
        
        purchase_receipt = frappe.get_doc("Purchase Receipt", r_name)
        
        l_costs = frappe.get_doc("Landed Costs", purchase_receipt.get("custom_landed_costs"))
        
        # Create a new Landed Cost Voucher document
        new_lcv = frappe.new_doc("Landed Cost Voucher")
        new_lcv.company = purchase_receipt.get("company")
        new_lcv.posting_date = purchase_receipt.get("posting_date")
    
        # Append to 'purchase_receipts' table within Landed Cost Voucher
        new_lcv.append("purchase_receipts", {
            "receipt_document_type": "Purchase Receipt",
            "receipt_document": purchase_receipt.get("name"),
            "supplier": purchase_receipt.get("supplier"),
            "grand_total": purchase_receipt.get("grand_total"),
            "distribute_charges_based_on": "Qty"
        })

        # Append items from Purchase Receipt to LCV
        for pr in new_lcv.get("purchase_receipts"):
            pr_items = get_pr_items(pr)
            for d in pr_items:
                item = new_lcv.append("items")
                item.item_code = d.item_code
                item.description = d.description
                item.qty = d.qty
                item.rate = d.base_rate
                item.cost_center = d.cost_center
                item.amount = d.base_amount
                item.receipt_document_type = pr.receipt_document_type
                item.receipt_document = pr.receipt_document
                item.purchase_receipt_item = d.name
                item.is_fixed_asset = d.is_fixed_asset
        
        
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
        frappe.db.commit()
             
        new_lcv.submit()        
    
        frappe.response['message'] = new_lcv.name
        
def get_pr_items(purchase_receipt):
	item = frappe.qb.DocType("Item")
	pr_item = frappe.qb.DocType(purchase_receipt.receipt_document_type + " Item")
	return (
		frappe.qb.from_(pr_item)
		.inner_join(item)
		.on(item.name == pr_item.item_code)
		.select(
			pr_item.item_code,
			pr_item.description,
			pr_item.qty,
			pr_item.base_rate,
			pr_item.base_amount,
			pr_item.name,
			pr_item.cost_center,
			pr_item.is_fixed_asset,
			ConstantColumn(purchase_receipt.receipt_document_type).as_("receipt_document_type"),
			ConstantColumn(purchase_receipt.receipt_document).as_("receipt_document"),
		)
		.where(
			(pr_item.parent == purchase_receipt.receipt_document)
			& ((item.is_stock_item == 1) | (item.is_fixed_asset == 1))
		)
		.run(as_dict=True)
	)
