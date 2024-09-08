// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Mpesa To Bank Sweep', {
	fetch_mpesa_accounts(frm) {
		frappe.call({
            method: 'get_mpesa_accounts',
            args: {
                message: {
                    default_account: frm.doc.default_account_paid_to,
                    company: frm.doc.company,
                    mpesa_parent: frm.doc.parent_account_for_mpesa_accounts
                }
            },
    		callback: function(response) {
                console.log(response.message)
                let accounts = response.message;

                // Clear existing rows in the child table
                frm.get_field('items').grid.get_data().forEach(row => {
                    frm.get_field('items').grid.remove_row(row);
                });
                
                // Add new rows for each entry in the accounts array
                accounts.forEach(account => {
                    let row = frm.add_child('items');
                    // Set the values in each row as needed
                    row.account_paid_from = account.from_account; // Example; adjust according to your data structure
                    row.account_paid_to = account.to_account; 
                    row.mode_of_payment = account.mode_of_payment; 
                    
                });
                
                // Refresh the child table field to show the updated rows
                frm.refresh_field('items');
                frm.save()
            }
    	})
	},
	sweep(frm) {
        frappe.call({
                method: 'sweep_account',
        		callback: function(response) {
                    console.log(response.message)
                    let accounts = response.message;
        		}
        })
    }
})

frappe.ui.form.on('Midnight Sweep Item', {
    // cdt is Child DocType name i.e. Midnight Sweep Item
    // cdn is the row name e.g. bbfcb8da6a
    account_paid_from(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (frm.doc.default_account_paid_to) {
            frappe.model.set_value(cdt, cdn, 'account_paid_to', frm.doc.default_account_paid_to);
        }
        
        set_mode_of_payment(frm, cdt, cdn, row.account_paid_from, frm.doc.company);
    }
});

function set_mode_of_payment(frm, cdt, cdn, account_paid_from, company) {
    if (account_paid_from) {
        // Fetch the Mode of Payment where the default_account matches account_paid_from
        frappe.call({
            method: 'get_mode_of_payment',
            args: {
                message: {
                    default_account: account_paid_from,
                    company: company
                }
            },
            callback: function(response) {
                if (response.message && response.message != "ok") {
                    let mode_of_payment = response.message;
                    frappe.model.set_value(cdt, cdn, 'mode_of_payment', mode_of_payment);
                }
            }
        });
    }
}