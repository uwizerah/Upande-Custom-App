// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Bank Bulk Upload"] = {
	"filters": [
		{
			fieldname: 'parent',
			label: 'Parent',
			fieldtype: 'Data',
			read_only: 1,
			// default: frappe.defaults.get_user_default('company')
		},
	]
};
