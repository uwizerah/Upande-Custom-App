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
                reference,
                beneficiary_name,
                bank_account,
                account_number,
                bank_code,
                branch_code,
                amount,
                swift_code,
                currency             
            FROM
                `tabRTGS Bulk Upload Item`
            WHERE
                `tabRTGS Bulk Upload Item`.parent = %(parent)s
            """
            
    # Use the frappe.db.sql method to execute the query safely
    data = frappe.db.sql(query, {"parent": parent}, as_dict=True)
        
    return data

def get_columns(filters=None):
    columns = [
        {"label": "Payment Reference", "fieldname": "reference", "fieldtype": "Data", "width": 150, "align": "center"},
        {"label": "Beneficiary Name", "fieldname": "beneficiary_name", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Bank Name", "fieldname": "bank_account", "fieldtype": "Data", "width": 180, "align": "center"},
        {"label": "Account Number", "fieldname": "account_number", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": "Bank Code", "fieldname": "bank_code", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Branch Code", "fieldname": "branch_code", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150, "align": "center"},
        {"label": "Swift Code", "fieldname": "swift_code", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Data", "width": 80, "align": "center"}
    ]
 
    return columns


