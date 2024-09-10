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
                payment_reference,
                beneficiary_name,
                bank_account,
                account_number,
                bank_code,
                branch_code,
                amount
            FROM
                `tabBank Bulk Upload Item`
            WHERE
                `tabBank Bulk Upload Item`.parent = %(parent)s
            """
            
    # Use the frappe.db.sql method to execute the query safely
    data = frappe.db.sql(query, {"parent": parent}, as_dict=True)
        
    return data

def get_columns(filters=None):
    columns = [
        {"label": "Payment Reference", "fieldname": "payment_reference", "fieldtype": "Data", "width": 150},
        {"label": "Beneficiary Name", "fieldname": "beneficiary_name", "fieldtype": "Data", "width": 200},
        {"label": "Bank Name", "fieldname": "bank_account", "fieldtype": "Data", "width": 180},
        {"label": "Account Number", "fieldname": "account_number", "fieldtype": "Data", "width": 80},
        {"label": "Bank Code", "fieldname": "bank_code", "fieldtype": "Data", "width": 120},
        {"label": "Branch Code", "fieldname": "branch_code", "fieldtype": "Data", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
    ]
 
    return columns

