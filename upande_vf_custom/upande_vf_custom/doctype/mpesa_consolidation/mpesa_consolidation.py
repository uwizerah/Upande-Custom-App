# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MpesaConsolidation(Document):
    @frappe.whitelist()
    def get_mpesa_accounts(self):
        result_data = []
        used_accounts = self.accounts_in_use()
        if self.mpesa_parent_account:
            mpesa_accounts = frappe.db.get_all("Account", filters = {"parent_account": self.mpesa_parent_account, "custom_is_consolidation_account": 0}, fields=["name"])

            if mpesa_accounts:
                for account in mpesa_accounts:
                    if not account.get("name") in used_accounts:
                        acc_dict = {
                            "from_account": account.get("name"),
                            "to_account": self.consolidation_account,
                        }
            
                        if not acc_dict in result_data:
                            result_data.append(acc_dict)
        return result_data
    
    def accounts_in_use(self):
        doc_list = []
        s_docs = frappe.db.get_all("Mpesa Consolidation Item", filters=None, fields=["account_paid_from"])
        if s_docs:
            for s_doc in s_docs:
                doc_list.append(s_doc.get("account_paid_from"))
                
        return doc_list
         
def create_mpesa_to_cons_sweep_journal():  
    sweep_items = "Mpesa Consolidation Item"
    create_mpesa_sweep_journal(sweep_items)  
     
def create_mpesa_sweep_journal(sweep_items):
    # Fetch balances from the script
    balances = get_account_balances(sweep_items)
    
    if balances:
        comb_accs = balances[0]  # Dictionary of accounts
        
        # for key, value in cum_bal.items():
        # Iterate through each key account and its corresponding debit accounts
        for debit_account, credit_accounts in comb_accs.items():
            company = frappe.db.get_value("Account", debit_account, "company")
            # Create a new Journal Entry document for each key account
            je_doc = frappe.get_doc({
                "doctype": "Journal Entry",
                "company": company,
                "posting_date": frappe.utils.today(),
                "custom_mpesa_sweep": 1,
                "voucher_type": "Journal Entry",  # Use the appropriate voucher type if different
                "accounts": []
            })

            # Calculate the total debit amount
            total_debit_amount = sum(credit_accounts.values())
            
            if total_debit_amount > 0:

                # Add credit entry for the key account
                je_doc.append("accounts", {
                    "account": debit_account,
                    "debit_in_account_currency": total_debit_amount
                })

                # Add debit entries for each debit account
                for credit_account, amount in credit_accounts.items():
                    if amount > 0:
                        je_doc.append("accounts", {
                            "account": credit_account,
                            "credit_in_account_currency": amount
                        })
                        
                # Save and submit the Journal Entry
                je_doc.save()
                frappe.db.commit()
                je_doc.submit()

def get_account_balances(sweep_items):
    # Fetch all Mpesa Consolidation Item records
    s_docs = frappe.db.get_all(sweep_items, filters=None, fields=["account_paid_from", "account_paid_to"])
    bal_dict = {}

    # Construct the dictionary with balances
    if s_docs:
        for s_doc in s_docs:
            account_paid_to = s_doc.get("account_paid_to")
            account_paid_from = s_doc.get("account_paid_from")

            # Initialize the dictionary for 'account_paid_to' if it doesn't exist
            if account_paid_to not in bal_dict:
                bal_dict[account_paid_to] = {}

            # Get the account balance for 'account_paid_from'
            account_balance = frappe.db.sql("""
                SELECT 
                    SUM(debit) - SUM(credit) AS balance
                FROM 
                    `tabGL Entry`
                WHERE 
                    account = %s AND posting_date <= %s
            """, (account_paid_from, frappe.utils.today()), as_dict=True)

            # Extract balance value and handle NoneType
            balance = account_balance[0]["balance"] if account_balance else 0
            balance = balance if balance is not None else 0  # Convert None to 0

            # Assign the account_paid_from and balance to the dictionary
            bal_dict[account_paid_to][account_paid_from] = balance

    # Dictionary to store sums for each 'account_paid_to'
    balance_sums = {}

    # Calculate the sum of balances for each 'account_paid_to'
    for account_paid_to, inner_dict in bal_dict.items():
        # Sum all balances in the inner dictionary, handling NoneType
        balance_sum = sum(value if value is not None else 0 for value in inner_dict.values())

        # Store the sum in the 'balance_sums' dictionary
        balance_sums[account_paid_to] = balance_sum
        
    # Return both the detailed balances and the sums
    return bal_dict, balance_sums

