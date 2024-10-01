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
                "reference",
				"debit_amount",
				"payment_type",
				"beneficiary_name",
				"beneficiary_account",
				"network_type",
				"swift_code",
				"beneficiary_email_id",
				"beneficiary_address_1",
				"beneficiary_address_2",
				"beneficiary_address_3",
				"beneficiary_address_4",
				"charge_bearer",
				"debit_narrative",
				"credit_narrative",
				"deal_reference_number"             
            FROM
                `tabInternational Payments Bulk Upload Item`
            WHERE
                `tabInternational Payments Bulk Upload Item`.parent = %(parent)s
            """
            
    # Use the frappe.db.sql method to execute the query safely
    data = frappe.db.sql(query, {"parent": parent}, as_dict=True)
        
    return data

def get_columns(filters=None):
    columns = [
        {"label": "Payment Reference", "fieldname": "reference","fieldtype": "Data", "width": 150, "align": "center"},
        {"label": "Debit Amount", "fieldname": "debit_amount", "fieldtype": "float", "width": 150, "align": "center"},
        {"label": "Payment Type", "fieldname": "payment_type", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": "Beneficiary Name", "fieldname": "beneficiary_name", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Beneficiary Account", "fieldname": "beneficiary_account", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Network Type", "fieldname": "network_type", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Swift Code", "fieldname": "swift_code", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Beneficiary Email ID", "fieldname": "beneficiary_email_id", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Beneficiary Address 1", "fieldname": "beneficiary_address_1", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Beneficiary Address 2", "fieldname": "beneficiary_address_2", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Beneficiary Address 3", "fieldname": "beneficiary_address_3", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Beneficiary Address 4", "fieldname": "beneficiary_address_4", "fieldtype": "Data", "width": 200, "align": "center"},
        {"label": "Charge Bearer", "fieldname": "charge_bearer", "fieldtype": "Data", "width": 180, "align": "center"},
        {"label": "Debit Narrative", "fieldname": "daily_narrative", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Credit Narrative", "fieldname": "credit_narrative", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": "Deal Reference Number", "fieldname": "deal_reference_number", "fieldtype": "Data", "width": 120, "align": "center"}
    ]
 
    return columns

