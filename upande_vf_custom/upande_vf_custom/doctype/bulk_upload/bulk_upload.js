// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Upload', {
	get_draft_payments(frm) {
        frappe.call({
            method: 'get_pending_payments',
            doc: frm.doc,
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                if (r.message) {
                    if(frm.doc.type=="EFT"){
                        processEFTDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                    }else if(frm.doc.type=="RTGS"){
                        processRTGSDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                    }
                    else if(frm.doc.type=="International Payments"){
                        processIPDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                    }
                    else if(frm.doc.type=="Mpesa"){
                        processMpesaDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                    }
                    
                    
                } else {
                    console.log("No Draft Payments Match The Criteria.");
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
            doc: frm.doc,
            callback: function(r) {
                if(r.message) {
                    console.log(r.message)
                    window.open(r.message);
                }
            }
        });
        
    }
});


function processEFTDraftPayments(frm, draftPymnts, grand_totals) {
    const childTableField = 'eft_upload_items'; // Update this with the actual field name of your child table

    // Create a set of existing entries to check for duplicates
    const existingPymnts = new Set(frm.doc[childTableField].map(row => row.payment_reference)); // Assuming 'payment_reference' is a field in the child table
    draftPymnts.forEach(dp => {
         if (!existingPymnts.has(dp.name)) {
            let newRow = frm.add_child(childTableField);
            newRow.payment_reference = dp.name; // Assuming 'payment_reference' is a field in the child table
            newRow.beneficiary_name = dp.party; // Assuming 'beneficiary_name' is a field in the child table
            newRow.bank_account = dp.bank_name;
            newRow.amount = dp.paid_amount; // Assuming 'amount' is a field in the child table
            existingPymnts.add(dp.name); // Add the new purchase order to the set of existing orders
        }
    });
    
    frm.doc.total_amount = grand_totals
    
    frm.refresh_field(childTableField); // Refresh the child table field to display the added rows
    frm.refresh_field('total_amount')
    frm.save()
}
function processRTGSDraftPayments(frm, draftPymnts, grand_totals) {
    const childTableField = 'rtgs_bulk_upload_items'; // Update this with the actual field name of your child table

    // Create a set of existing entries to check for duplicates
    const existingPymnts = new Set(frm.doc[childTableField].map(row => row.payment_reference)); // Assuming 'payment_reference' is a field in the child table
    draftPymnts.forEach(dp => {
         if (!existingPymnts.has(dp.name)) {
            let newRow = frm.add_child(childTableField);
            newRow.payment_reference = dp.name; // Assuming 'payment_reference' is a field in the child table
            newRow.beneficiary_name = dp.party; // Assuming 'beneficiary_name' is a field in the child table
            newRow.bank_account = dp.bank_name;
            newRow.amount = dp.paid_amount; // Assuming 'amount' is a field in the child table
            existingPymnts.add(dp.name); // Add the new purchase order to the set of existing orders
        }
    });
    
    frm.doc.total_amount = grand_totals
    
    frm.refresh_field(childTableField); // Refresh the child table field to display the added rows
    frm.refresh_field('total_amount')
    frm.save()
}
function processIPDraftPayments(frm, draftPymnts, grand_totals) {
    const childTableField = 'international_payments_bulk_upload_items'; // Update this with the actual field name of your child table

    // Create a set of existing entries to check for duplicates
    const existingPymnts = new Set(frm.doc[childTableField].map(row => row.payment_reference)); // Assuming 'payment_reference' is a field in the child table
    draftPymnts.forEach(dp => {
         if (!existingPymnts.has(dp.name)) {
            let newRow = frm.add_child(childTableField);
            newRow.payment_reference = dp.name; // Assuming 'payment_reference' is a field in the child table
            newRow.beneficiary_name = dp.party; // Assuming 'beneficiary_name' is a field in the child table
            newRow.bank_account = dp.bank_name;
            newRow.amount = dp.paid_amount; // Assuming 'amount' is a field in the child table
            existingPymnts.add(dp.name); // Add the new purchase order to the set of existing orders
        }
    });
    
    frm.doc.total_amount = grand_totals
    
    frm.refresh_field(childTableField); // Refresh the child table field to display the added rows
    frm.refresh_field('total_amount')
    frm.save()
}
function processMpesaDraftPayments(frm, draftPymnts, grand_totals) {
    const childTableField = 'mpesa_bulk_upload_items'; // Update this with the actual field name of your child table

    // Create a set of existing entries to check for duplicates
    const existingPymnts = new Set(frm.doc[childTableField].map(row => row.payment_reference)); // Assuming 'payment_reference' is a field in the child table
    draftPymnts.forEach(dp => {
         if (!existingPymnts.has(dp.name)) {
            let newRow = frm.add_child(childTableField);
            newRow.payment_reference = dp.name; // Assuming 'payment_reference' is a field in the child table
            newRow.beneficiary_name = dp.party; // Assuming 'beneficiary_name' is a field in the child table
            newRow.bank_account = dp.bank_name;
            newRow.amount = dp.paid_amount; // Assuming 'amount' is a field in the child table
            existingPymnts.add(dp.name); // Add the new purchase order to the set of existing orders
        }
    });
    
    frm.doc.total_amount = grand_totals
    
    frm.refresh_field(childTableField); // Refresh the child table field to display the added rows
    frm.refresh_field('total_amount')
    frm.save()
}