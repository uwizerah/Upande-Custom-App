import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
    get_columns,
    filter_accounts,
    set_gl_entries_by_account,
    filter_out_zero_value_rows,
    add_total_row,
    get_appropriate_currency,
    get_filtered_list_for_consolidated_report,
    get_period_list,
)

def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )
    
    net_profit_loss = get_net_profit_loss(
        income, expense, period_list, filters.company, filters.presentation_currency
    )

    data = []
    data.extend(income or [])
    data.extend(expense or [])
    if net_profit_loss:
        data.append(net_profit_loss)

    columns = get_columns(
        filters.periodicity, period_list, filters.accumulated_values, filters.company
    )
 
    custom_column = {"label": "Budget", "fieldname": "budget", "fieldtype": "Currency"}
    columns.append(custom_column)

    # chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

    currency = filters.presentation_currency or frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )
    report_summary = get_report_summary(
        period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
    )

    return columns, data, None, None, report_summary


def get_report_summary(
    period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
    net_income, net_expense, net_profit = 0.0, 0.0, 0.0

    # from consolidated financial statement
    if filters.get("accumulated_in_group_company"):
        period_list = get_filtered_list_for_consolidated_report(filters, period_list)

    for period in period_list:
        key = period if consolidated else period.key
        if income:
            net_income += income[-2].get(key)
        if expense:
            net_expense += expense[-2].get(key)
        if net_profit_loss:
            net_profit += net_profit_loss.get(key)

    if len(period_list) == 1 and periodicity == "Yearly":
        profit_label = _("Profit This Year")
        income_label = _("Total Income This Year")
        expense_label = _("Total Expense This Year")
    else:
        profit_label = _("Net Profit")
        income_label = _("Total Income")
        expense_label = _("Total Expense")

    return [
        {"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "-"},
        {"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "=", "color": "blue"},
        {
            "value": net_profit,
            "indicator": "Green" if net_profit > 0 else "Red",
            "label": profit_label,
            "datatype": "Currency",
            "currency": currency,
        },
    ]


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
    total = 0
    net_profit_loss = {
        "account_name": "'" + _("Profit for the year") + "'",
        "account": "'" + _("Profit for the year") + "'",
        "warn_if_negative": True,
        "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
    }

    has_value = False

    for period in period_list:
        key = period if consolidated else period.key
        total_income = flt(income[-2][key], 3) if income else 0
        total_expense = flt(expense[-2][key], 3) if expense else 0

        net_profit_loss[key] = total_income - total_expense

        if net_profit_loss[key]:
            has_value = True

        total += flt(net_profit_loss[key])
        net_profit_loss["total"] = total

    if has_value:
        return net_profit_loss


def get_chart_data(filters, columns, income, expense, net_profit_loss):
    labels = [d.get("label") for d in columns[2:] if not d.get("label")=="Budget"]

    income_data, expense_data, net_profit = [], [], []

    for p in columns[2:]:
        if income:
            income_data.append(income[-2].get(p.get("fieldname")))
        if expense:
            expense_data.append(expense[-2].get(p.get("fieldname")))
        if net_profit_loss:
            net_profit.append(net_profit_loss.get(p.get("fieldname")))

    datasets = []
    if income_data:
        datasets.append({"name": _("Income"), "values": income_data})
    if expense_data:
        datasets.append({"name": _("Expense"), "values": expense_data})
    if net_profit:
        datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

    chart = {"data": {"labels": labels, "datasets": datasets}}

    if not filters.accumulated_values:
        chart["type"] = "bar"
    else:
        chart["type"] = "line"

    chart["fieldtype"] = "Currency"

    return chart

# def get_budget_data(start, end):
#     pl_accs_list = []
#     bal_dict = {}
    
#     pl_accounts = frappe.db.get_all("Account", filters={"report_type": "Profit and Loss"}, fields=["name"])

#     if pl_accounts:
#         for acc in pl_accounts:
#             if not acc.get("name") in pl_accs_list:
#                 pl_accs_list.append(acc.get("name"))
                
#     # for acc_name in pl_accs_list:
#     monthly_distribution = frappe.db.get_all("VF Monthly Distribution Percentage", filters={"parenttype": "Budget", "start_date": [">=", start], "end_date": ["<=", end]}, fields=["amount", "parent", "account"])
#     if monthly_distribution:
#         for md in monthly_distribution:
#             check_if_parent_is_closed = frappe.db.get_value("Budget", md.get("parent"), "docstatus")
#             if check_if_parent_is_closed == 1:
#                 if not md.get("account") in bal_dict.keys():
#                     bal_dict[md.get("account")] = 0
                
#                 bal_dict[md.get("account")] += md.get("amount")
               
#     return bal_dict

def get_budget_data(start, end):
    # Fetch monthly distributions with necessary account and parent budget details in a single query
    monthly_distribution = frappe.db.sql(
        """
        SELECT 
            md.amount,
            md.account,
            b.docstatus
        FROM 
            `tabVF Monthly Distribution Percentage` AS md
        JOIN 
            `tabBudget` AS b ON md.parent = b.name
        JOIN 
            `tabAccount` AS acc ON md.account = acc.name
        WHERE 
            md.parenttype = 'Budget' 
            AND md.start_date >= %s 
            AND md.end_date <= %s
            AND acc.report_type = 'Profit and Loss'
        """,
        (start, end),
        as_dict=True
    )
    
    # Process results and aggregate amounts
    bal_dict = {}
    for md in monthly_distribution:
        if md.docstatus == 1:  # Only process closed budgets
            bal_dict[md.account] = bal_dict.get(md.account, 0) + md.amount

    return bal_dict


def get_data(
    company,
    root_type,
    balance_must_be,
    period_list,
    filters=None,
    accumulated_values=1,
    only_current_fiscal_year=True,
    ignore_closing_entries=False,
    ignore_accumulated_values_for_fy=False,
    total=True,
):

    accounts = get_accounts(company, root_type)

    if not accounts:
        return None

    accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

    company_currency = get_appropriate_currency(company, filters)

    gl_entries_by_account = {}
    for root in frappe.db.sql(
        """select lft, rgt from tabAccount
            where root_type=%s and ifnull(parent_account, '') = ''""",
        root_type,
        as_dict=1,
    ):

        set_gl_entries_by_account(
            company,
            period_list[0]["year_start_date"] if only_current_fiscal_year else None,
            period_list[-1]["to_date"],
            root.lft,
            root.rgt,
            filters,
            gl_entries_by_account,
            ignore_closing_entries=ignore_closing_entries,
            root_type=root_type,
        )

    calculate_values(
        accounts_by_name,
        gl_entries_by_account,
        period_list,
        accumulated_values,
        ignore_accumulated_values_for_fy,
    )
    accumulate_values_into_parents(accounts, accounts_by_name, period_list)
    out = prepare_data(accounts, balance_must_be, period_list, company_currency)
    out = filter_out_zero_value_rows(out, parent_children_map)

    if out and total:
        add_total_row(out, root_type, balance_must_be, period_list, company_currency)

    return out

def prepare_data(accounts, balance_must_be, period_list, company_currency):
    data = []
    print("p"*80)
    print(period_list)
    year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
    year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")
    budget = get_budget_data(year_start_date, year_end_date)
    
    for k,v in budget.items():
        for acc in accounts:
            if acc.get("name") == k:
                acc["budget"] = v
    
    for d in accounts:
        # add to output
        has_value = False
        total = 0
        row = frappe._dict(
            {
                "account": _(d.name),
                "parent_account": _(d.parent_account) if d.parent_account else "",
                "indent": flt(d.indent),
                "year_start_date": year_start_date,
                "budget": d.get("budget"),
                "year_end_date": year_end_date,
                "currency": company_currency,
                "include_in_gross": d.include_in_gross,
                "account_type": d.account_type,
                "is_group": d.is_group,
                "opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be == "Debit" else -1),
                "account_name": (
                    "%s - %s" % (_(d.account_number), _(d.account_name))
                    if d.account_number
                    else _(d.account_name)
                ),
            }
        )
        for period in period_list:
            if d.get(period.key) and balance_must_be == "Credit":
                # change sign based on Debit or Credit, since calculation is done using (debit - credit)
                d[period.key] *= -1

            row[period.key] = flt(d.get(period.key, 0.0), 3)

            if abs(row[period.key]) >= 0.005:
                # ignore zero values
                has_value = True
                total += flt(row[period.key])

        row["has_value"] = has_value
        row["total"] = total
        data.append(row)

    return data

def calculate_values(
    accounts_by_name,
    gl_entries_by_account,
    period_list,
    accumulated_values,
    ignore_accumulated_values_for_fy,
):
    for entries in gl_entries_by_account.values():
        for entry in entries:
            d = accounts_by_name.get(entry.account)
            if not d:
                frappe.msgprint(
                    _("Could not retrieve information for {0}.").format(entry.account),
                    title="Error",
                    raise_exception=1,
                )
            for period in period_list:
                # check if posting date is within the period

                if entry.posting_date <= period.to_date:
                    if (accumulated_values or entry.posting_date >= period.from_date) and (
                        not ignore_accumulated_values_for_fy
                        or entry.fiscal_year == period.to_date_fiscal_year
                    ):
                        d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

            if entry.posting_date < period_list[0].year_start_date:
                d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)
                d["budget"] = 0
            
            budget = get_budget_data(period_list[0]["from_date"], period_list[0]["to_date"])
            for k,v in budget.items():
                if d.get("name") == k:
                    d["budget"] = v
    
def accumulate_values_into_parents(accounts, accounts_by_name, period_list):
    """accumulate children's values in parent accounts"""
    for d in reversed(accounts):
        if d.parent_account:
            for period in period_list:
                accounts_by_name[d.parent_account][period.key] = accounts_by_name[d.parent_account].get(
                    period.key, 0.0
                ) + d.get(period.key, 0.0)
                
            accounts_by_name[d.parent_account]["opening_balance"] = accounts_by_name[d.parent_account].get(
                "opening_balance", 0.0
            ) + d.get("opening_balance", 0.0)
            
            accounts_by_name[d.parent_account]["budget"] = accounts_by_name[d.parent_account].get(
                "budget", 0.0
            ) + d.get("budget", 0.0)

def get_accounts(company, root_type):
	return frappe.db.sql(
		"""
		select name, account_number, parent_account, lft, rgt, root_type, report_type, account_name, include_in_gross, account_type, is_group, lft, rgt
		from `tabAccount`
		where company=%s and root_type=%s order by lft""",
		(company, root_type),
		as_dict=True,
	)
