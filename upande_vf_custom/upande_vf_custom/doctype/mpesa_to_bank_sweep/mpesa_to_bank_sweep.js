// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Mpesa To Bank Sweep', {
	sweep_accounts(frm) {
        frappe.call({
                method: 'create_mpesa_to_bank_sweep_journal',
                doc: frm.doc,
        		callback: function(response) {
                    return
        		}
        })
    }
})

