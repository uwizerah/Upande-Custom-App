import csv
import frappe

def get_account_balances_for_h1(date):
    """
    Fetches the current balances for a list of accounts in ERPNext as of a specific date.

    :return: Dictionary with account names, balances, and the specified date
    """
    account_list = h1_accounts()
    
    company = "Victory Farms Ltd"
    # date = "2024-10-05"  # Specify the date for which balances are to be fetched

    if not account_list or not company or not date:
        raise ValueError("Account list, company, and date are required.")

    # Define the file path for the CSV
    file_path = frappe.get_site_path('private', 'files', 'sweep', 'h1sweep', date + '-H1' +'.csv')
    
    account_balances = []

    for account in account_list:
        try:
            # Fetch account balance using the General Ledger table
            balance = frappe.db.sql("""
                SELECT SUM(debit) - SUM(credit) AS balance
                FROM `tabGL Entry`
                WHERE account = %s AND company = %s AND posting_date = %s AND is_cancelled = 0
            """, (account, company, date), as_dict=True)

            account_balances.append({
                "Account": account,
                "Balance": balance[0].get("balance", 0.0) if balance else 0.0,
                "Date": date
            })
        except Exception as e:
            frappe.log_error(f"Error fetching balance for account {account}: {e}", "Account Balance Error")
            account_balances.append({
                "Account": account,
                "Balance": None,
                "Date": date
            })
    
    # Write the data to a CSV file
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Account", "Balance", "Date"])
        writer.writeheader()
        writer.writerows(account_balances)

    return file_path

def get_account_balances_for_h2(date):
    """
    Fetches the current balances for a list of accounts in ERPNext as of a specific date.

    :return: Dictionary with account names, balances, and the specified date
    """
    account_list = h2_accounts()
    
    company = "Victory Farms Ltd"
    # date = "2024-10-05"  # Specify the date for which balances are to be fetched

    if not account_list or not company or not date:
        raise ValueError("Account list, company, and date are required.")

    # Define the file path for the CSV
    file_path = frappe.get_site_path('private', 'files', 'sweep', 'h2sweep', date + '-H2' +'.csv')
    
    account_balances = []

    for account in account_list:
        try:
            # Fetch account balance using the General Ledger table
            balance = frappe.db.sql("""
                SELECT SUM(debit) - SUM(credit) AS balance
                FROM `tabGL Entry`
                WHERE account = %s AND company = %s AND posting_date = %s AND is_cancelled = 0
            """, (account, company, date), as_dict=True)

            account_balances.append({
                "Account": account,
                "Balance": balance[0].get("balance", 0.0) if balance else 0.0,
                "Date": date
            })
        except Exception as e:
            frappe.log_error(f"Error fetching balance for account {account}: {e}", "Account Balance Error")
            account_balances.append({
                "Account": account,
                "Balance": None,
                "Date": date
            })
    
    # Write the data to a CSV file
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Account", "Balance", "Date"])
        writer.writeheader()
        writer.writerows(account_balances)

    return file_path

def h1_accounts():
    h1_list = []
    mpesa_h1_acc = frappe.get_doc("Mpesa Consolidation", "Mpesa H1 - VFL")
    
    if mpesa_h1_acc:
        for item in mpesa_h1_acc.items:
            if not item.get("account_paid_from") in h1_list:
                h1_list.append(item.get("account_paid_from"))
            
        return h1_list
    
def h2_accounts():
    h2_list = []
    mpesa_h2_acc = frappe.get_doc("Mpesa Consolidation", "Mpesa H2 - VFL")
    
    if mpesa_h2_acc:
        for item in mpesa_h2_acc.items:
            if not item.get("account_paid_from") in h2_list:
                h2_list.append(item.get("account_paid_from"))
            
        return h2_list