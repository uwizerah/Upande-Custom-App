// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mpesa Consolidation', {
	fetch_mpesa_accounts(frm) {
		frappe.call({
            method: 'get_mpesa_accounts',
            doc: frm.doc,
    		callback: function(response) {
                console.log(response.message)
                let accounts = response.message;

                // Add new rows for each entry in the accounts array
                accounts.forEach(account => {
                    let row = frm.add_child('items');
                    // Set the values in each row as needed
                    row.account_paid_from = account.from_account; // Example; adjust according to your data structure
                    row.account_paid_to = account.to_account; 
                    
                });
                
                // Refresh the child table field to show the updated rows
                frm.refresh_field('items');
                frm.save()
            }
    	})
	},
	sweep_accounts(frm) {
        frappe.call({
                method: 'create_mpesa_to_cons_sweep_journal',
                doc: frm.doc,
        		callback: function(response) {
                    return
        		}
        })
    }
})

frappe.ui.form.on('Mpesa Consolidation Item', {
    // cdt is Child DocType name i.e. Midnight Sweep Item
    // cdn is the row name e.g. bbfcb8da6a
    account_paid_from(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (frm.doc.consolidation_account) {
            frappe.model.set_value(cdt, cdn, 'account_paid_to', frm.doc.consolidation_account);
        }
        
    }
});

