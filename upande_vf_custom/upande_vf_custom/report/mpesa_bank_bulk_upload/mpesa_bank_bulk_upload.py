# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    data = get_data(filters=filters)
    columns = get_columns(filters=filters)
    
    return columns, data

def get_data(filters):
    parent = filters.get("parent")
    query = """
            SELECT
                "payment_reference",
                "mobilenumber",
				"documenttype",
				"supplier_invoice",
				"amount",
				"purposeofpayment",
				"beneficiary_name"
            FROM
                `tabMpesa Bulk Upload Item`
            WHERE
                `tabMpesa Bulk Upload Item`.parent = %(parent)s
            """
            
    # Use the frappe.db.sql method to execute the query safely
    data = frappe.db.sql(query, {"parent": parent}, as_dict=True)
        
    return data

def get_columns(filters=None):
    columns = [
        {"label": "MobileNumber", "fieldname": "mobilenumber", "fieldtype": "Data", "width": 170, "align": "center"},
        {"label": "DocumentType", "fieldname": "documenttype", "fieldtype": "Data", "width": 280, "align": "center"},
        {"label": "DocumentNumber", "fieldname": "supplier_invoice", "fieldtype": "Data", "width": 180, "align": "center"},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 180, "align": "center"},
        {"label": "PurposeOfPayment", "fieldname": "purposeofpayment", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Name", "fieldname": "beneficiary_name", "fieldtype": "Data", "width": 120, "align": "center"}
    ]
 
    return columns