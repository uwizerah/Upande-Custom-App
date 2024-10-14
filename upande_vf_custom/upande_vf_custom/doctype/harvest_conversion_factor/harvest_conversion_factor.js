// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Harvest Conversion Factor", {
    onload(frm) {
        frm.set_query('lake_warehouse', function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
    },

	start_of_the_year(frm) {
        frappe.call({
            method: 'get_end_date',
            doc: frm.doc,
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                if(r.message){
                    let response = r.message
                    frm.doc.end_of_the_year = response

                    frm.refresh_field("end_of_the_year")
                }
                
            }
        })
	},
});
