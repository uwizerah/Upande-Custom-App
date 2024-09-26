# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import copy
from collections import OrderedDict

import frappe
from frappe import _, qb
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	if not filters:
		return [], [], None, []

	validate_filters(filters)

	columns = get_columns(filters)
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)
	# print("*"*80)
	# print(data)

	if not data:
		return [], [], None, []

	data, chart_data = prepare_data(data, filters)

	return columns, data, None, chart_data


def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date and to_date:
		frappe.throw(_("From and To Dates are required."))
	elif date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and so.transaction_date between %(from_date)s and %(to_date)s"

	if filters.get("company"):
		conditions += " and so.company = %(company)s"

	if filters.get("sales_order"):
		conditions += " and so.name in %(sales_order)s"

	return conditions


def get_data(conditions, filters):
	data = frappe.db.sql(
		"""
		SELECT
			so.transaction_date as date,
			so.name as sales_order,
			so.customer_name as cust_name,
			IF(so.status in ('Completed','To Bill'), 0, (SELECT delay_days)) as delay,
			soi.qty, soi.delivered_qty,
			soi.uom as uom,
			(cni.qty) AS missed_qty,
			(cni.qty - dni.qty) AS lost_qty,
			IFNULL(SUM(sii.qty), 0) as billed_qty,
   			(soi.qty - dni.qty) as missing_qty,
			soi.base_amount as amount,
			(soi.delivered_qty * soi.base_rate) as delivered_qty_amount,
			(soi.billed_amt * IFNULL(so.conversion_rate, 1)) as billed_amount,
			(soi.base_amount - (soi.billed_amt * IFNULL(so.conversion_rate, 1))) as pending_amount,
			so.company, soi.name,
		FROM
			`tabSales Order` so,
			`tabSales Order Item` soi
		LEFT JOIN `tabSales Invoice Item` sii
			ON sii.so_detail = soi.name and sii.docstatus = 1
   		LEFT JOIN `tabConsignment Note Item` cni
			ON cni.so_detail = soi.name and cni.docstatus = 1
		LEFT JOIN `tabDelivery Note Item` dni
			ON dni.so_detail = soi.name and dni.docstatus = 1
		WHERE
			soi.parent = so.name
			and so.status not in ('Stopped', 'Closed', 'On Hold')
			and so.docstatus = 1
			{conditions}
		GROUP BY soi.name
		ORDER BY so.transaction_date ASC, soi.item_code ASC
	""".format(
			conditions=conditions
		),
		filters,
		as_dict=1,
	)

	return data

def prepare_data(data, filters):
	delivered, missed, lost = 0, 0, 0

	if filters.get("group_by_so"):
		sales_order_map = {}

	for row in data:
		# sum data for chart
		delivered += row["delivered_qty"] or 0
		missed += row["missing_qty"] or 0
		lost += row["lost_qty"] or 0

		# prepare data for report view
		row["qty_to_bill"] = flt(row["qty"]) - flt(row["billed_qty"])

		row["delay"] = 0 if row["delay"] and row["delay"] < 0 else row["delay"]

		

		if filters.get("group_by_so"):
			so_name = row["sales_order"]

			if not so_name in sales_order_map:
				# create an entry
				row_copy = copy.deepcopy(row)
				sales_order_map[so_name] = row_copy
			else:
				# update existing entry
				so_row = sales_order_map[so_name]
				so_row["required_date"] = max(getdate(so_row["delivery_date"]), getdate(row["delivery_date"]))
				so_row["delay"] = (
					min(so_row["delay"], row["delay"]) if row["delay"] and so_row["delay"] else so_row["delay"]
				)

				# sum numeric columns
				fields = [
					"qty",
					"delivered_qty",
					"missed_qty",
					"lost_qty",
					"billed_amount",
					"pending_amount",
				]
				for field in fields:
					so_row[field] = flt(row[field]) + flt(so_row[field])

	chart_data = prepare_chart_data(delivered, missed, lost)

	if filters.get("group_by_so"):
		data = []
		for so in sales_order_map:
			data.append(sales_order_map[so])
		return data, chart_data

	return data, chart_data


def prepare_chart_data(delivered, missed, lost):
	labels = ["Delivered Qty", "Unassigned Qty", "Delivery Variance"]

	return {
		"data": {"labels": labels, "datasets": [{"values": [delivered, missed, lost]}]},
		"type": "donut",
		"height": 300,
	}


def get_columns(filters):
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 120,
		},
		{
			"label": _("Customer Name"),
			"fieldname": "cust_name",
			"fieldtype": "Data",
			"width": 180,
		}
	]

	if not filters.get("group_by_so"):
		columns.append(
			{
				"label": _("Item Code"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 160,
			}
		)

	columns.extend(
		[
   			{
				"label": _("UOM"),
				"fieldname": "uom",
				"fieldtype": "Link",
				"options": "UOM",
				"width": 80
			},
			{
				"label": _("Ordered Qty"),
				"fieldname": "qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Packed Qty"),
				"fieldname": "missed_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Delivered Qty"),
				"fieldname": "delivered_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Delivery VAR"),
				"fieldname": "lost_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Qty Outstanding"),
				"fieldname": "missing_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			}
		]
	)

	return columns
