# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe import _, scrub
from frappe.utils import add_days, add_to_date, flt, getdate

from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
    return Analytics(filters).run()


class Analytics(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.date_field = (
            "posting_date"
        )
        self.months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        self.get_period_date_ranges()

    def run(self):
        self.get_columns()
        self.get_data()
        # self.get_chart_data()

        # Skipping total row for tree-view reports
        skip_total_row = 0

        if self.filters.tree_type in ["Territory"]:
            skip_total_row = 1

        return self.columns, self.data, None, None, None, skip_total_row

    def get_columns(self):
        self.columns = [
            {
                "label": _(self.filters.tree_type),
                "options": self.filters.tree_type,
                "fieldname": "entity",
                "fieldtype": "Link",
                "width": 140,
            }
        ]
    
        for end_date in self.periodic_daterange:
            period = self.get_period(end_date)
            self.columns.append(
                {"label": _(period), "fieldname": scrub(period), "fieldtype": "Float", "width": 120}
            )

        self.columns.append(
            {"label": _("Total"), "fieldname": "total", "fieldtype": "Float", "width": 120}
        )

    def get_data(self):
        if self.filters.tree_type in ["Territory"]:
            self.get_sales_transactions_based_on_customer_or_territory_group()
            self.get_rows_by_group()

    
    def get_sales_transactions_based_on_customer_or_territory_group(self):
        if self.filters["value_quantity"] == "Value":
            value_field = "base_net_total as value_field"
        else:
            value_field = "total_qty as value_field"

        entity_field = "custom_pos_territory as entity"

        self.entries = frappe.get_all(
            self.filters.doc_type,
            fields=[entity_field, value_field, self.date_field],
            filters={
                "docstatus": 1,
                "company": self.filters.company,
                self.date_field: ("between", [self.filters.from_date, self.filters.to_date]),
            },
        )
        print("*"*80)
        print(self.entries)
        print(entity_field)
        
        self.get_groups()


    def get_rows(self):
        self.data = []
        self.get_periodic_data()

        for entity, period_data in self.entity_periodic_data.items():
            row = {
                "entity": entity,
                "entity_name": self.entity_names.get(entity) if hasattr(self, "entity_names") else None,
            }
            total = 0
            for end_date in self.periodic_daterange:
                period = self.get_period(end_date)
                amount = flt(period_data.get(period, 0.0))
                row[scrub(period)] = amount
                total += amount

            row["total"] = total

            if self.filters.tree_type == "Item":
                row["stock_uom"] = period_data.get("stock_uom")

            self.data.append(row)

    def get_rows_by_group(self):
        self.get_periodic_data()
        out = []

        for d in reversed(self.group_entries):
            row = {"entity": d.name, "indent": self.depth_map.get(d.name)}
            total = 0
            for end_date in self.periodic_daterange:
                period = self.get_period(end_date)
                amount = flt(self.entity_periodic_data.get(d.name, {}).get(period, 0.0))
                row[scrub(period)] = amount
                if d.parent and (self.filters.tree_type != "Order Type" or d.parent == "Order Types"):
                    self.entity_periodic_data.setdefault(d.parent, frappe._dict()).setdefault(period, 0.0)
                    self.entity_periodic_data[d.parent][period] += amount
                total += amount

            row["total"] = total
            out = [row] + out

        self.data = out

    def get_periodic_data(self):
        self.entity_periodic_data = frappe._dict()

        for d in self.entries:
            if self.filters.tree_type == "Supplier Group":
                d.entity = self.parent_child_map.get(d.entity)
            period = self.get_period(d.get(self.date_field))
            self.entity_periodic_data.setdefault(d.entity, frappe._dict()).setdefault(period, 0.0)
            self.entity_periodic_data[d.entity][period] += flt(d.value_field)

            if self.filters.tree_type == "Item":
                self.entity_periodic_data[d.entity]["stock_uom"] = d.stock_uom

    def get_period(self, posting_date):
        if self.filters.range == "Weekly":
            period = _("Week {0} {1}").format(str(posting_date.isocalendar()[1]), str(posting_date.year))
        elif self.filters.range == "Monthly":
            period = _(str(self.months[posting_date.month - 1])) + " " + str(posting_date.year)
        elif self.filters.range == "Quarterly":
            period = _("Quarter {0} {1}").format(
                str(((posting_date.month - 1) // 3) + 1), str(posting_date.year)
            )
        else:
            year = get_fiscal_year(posting_date, company=self.filters.company)
            period = str(year[0])
        return period

    def get_period_date_ranges(self):
        from dateutil.relativedelta import MO, relativedelta

        from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)

        increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(
            self.filters.range, 1
        )

        if self.filters.range in ["Monthly", "Quarterly"]:
            from_date = from_date.replace(day=1)
        elif self.filters.range == "Yearly":
            from_date = get_fiscal_year(from_date)[1]
        else:
            from_date = from_date + relativedelta(from_date, weekday=MO(-1))

        self.periodic_daterange = []
        for dummy in range(1, 53):
            if self.filters.range == "Weekly":
                period_end_date = add_days(from_date, 6)
            else:
                period_end_date = add_to_date(from_date, months=increment, days=-1)

            if period_end_date > to_date:
                period_end_date = to_date

            self.periodic_daterange.append(period_end_date)

            from_date = add_days(period_end_date, 1)
            if period_end_date == to_date:
                break

    def get_groups(self):
        if self.filters.tree_type == "Territory":
            parent = "parent_territory"

        self.depth_map = frappe._dict()

        self.group_entries = frappe.db.sql(
            """select name, lft, rgt , {parent} as parent
            from `tab{tree}` order by lft""".format(
                tree="Territory", parent=parent
            ),
            as_dict=1,
        )

        for d in self.group_entries:
            if d.parent:
                self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
            else:
                self.depth_map.setdefault(d.name, 0)
    
    def get_chart_data(self):
        length = len(self.columns)

        labels = [d.get("label") for d in self.columns[1 : length - 1]]
        self.chart = {"data": {"labels": labels, "datasets": []}, "type": "line"}

        if self.filters["value_quantity"] == "Value":
            self.chart["fieldtype"] = "Currency"
        else:
            self.chart["fieldtype"] = "Float"
