// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Bulk Upload', {
	get_draft_payments(frm) {
	    console.log("hello")
        frappe.call({
            method: 'get_pending_payments',
            args: {
                doc: frm.doc.name
            },
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                if (r.message) {
                    console.log(r.message)

                    processDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                    
                } else {
                    console.log("No message received");
                }
            },
            error: (r) => {
                console.error("Error", r);
                // Handle the error here
            }
        })
    },
    
    download(frm) {
        frappe.call({
            method: 'download_report',
            args: {
                message:{
                    record: frm.doc
                    // file_path: frappe.get_site_path('private', 'files', frm.doc.name + '.csv')
                }
            },
            callback: function(r) {
                if(r.message) {
                    console.log(r.message)
                    window.open(r.message);
                }
            }
        });
        
    }
});


function processDraftPayments(frm, draftPymnts, grand_totals) {
    const childTableField = 'items'; // Update this with the actual field name of your child table
    // const existingOrders = new Set(frm.doc[childTableField].map(row => row.purchase_order)); // Assuming 'purchase_order' is a field in the child table
     // Initialize an array if the child table field is not present
    if (!frm.doc[childTableField]) {
        frm.doc[childTableField] = [];
    }

    // Create a set of existing entries to check for duplicates
    const existingPymnts = new Set(frm.doc[childTableField].map(row => row.payment_reference)); // Assuming 'payment_reference' is a field in the child table
    draftPymnts.forEach(dp => {
         if (!existingPymnts.has(dp.name)) {
            let newRow = frm.add_child(childTableField);
            newRow.payment_reference = dp.name; // Assuming 'payment_reference' is a field in the child table
            newRow.beneficiary_name = dp.party_name; // Assuming 'beneficiary_name' is a field in the child table
            newRow.bank_account = dp.bank_acc
            newRow.amount = dp.paid_amount; // Assuming 'amount' is a field in the child table
            existingPymnts.add(dp.name); // Add the new purchase order to the set of existing orders
        }
    });
    
    frm.doc.total_amount = grand_totals
    
    frm.refresh_field(childTableField); // Refresh the child table field to display the added rows
    frm.refresh_field('total_amount')
    frm.save()
}