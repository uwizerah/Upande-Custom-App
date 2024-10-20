import frappe

def on_submit(doc, method):
    if doc.custom_mpesa_sweep == 1:
        for item in doc.accounts:
            if item.get("debit_in_account_currency") > 0: 
                print("*"*80)
                print(item.get("account"), item.get("debit_in_account_currency"))
                # create_mpesa_sweep_journal(item.get("account"))
     
def create_mpesa_sweep_journal(account):
    # Fetch balances from the script
    balance = get_account_balances(account)
    print(balance)
    if balance:        
        # for key, value in cum_bal.items():
        # Iterate through each key account and its corresponding debit accounts
        for debit_account, credit_accounts in balance.items():
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

def get_account_balances(account_paid_from):
    # Fetch all Mpesa Consolidation Item records
    account = frappe.db.get_value("Mpesa To Bank Sweep Item", {"account_paid_from": account_paid_from}, "account_paid_to")
    bal_dict = {}
    
    # Construct the dictionary with balances
    if account:
        account_paid_to = account
        account_paid_from = account_paid_from

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
        
    return bal_dict

