// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["EFT Bank Bulk Upload"] = {
	// onload(report) {
	// 	// Ensure CSS is applied after the datatable is rendered
	// 	report.page.on('after-render', function() {
	// 		// Apply CSS to center-align the headers
	// 		$("th").css("text-align", "center");
	// 	});
	// },

	"filters": [
		{
			fieldname: 'parent',
			label: 'Parent',
			fieldtype: 'Data',
			read_only: 1,
		},
	]
};