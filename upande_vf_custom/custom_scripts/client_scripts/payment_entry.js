frappe.ui.form.on('Payment Entry', {
    onload(frm){
        if(frm.doc.status=='Submitted'){
            // frm.add_custom_button('Refresh', () => frm.refresh(), 'octicon octicon-sync', 'btn-secondary');
            frm.add_custom_button(__('Send Remittance Advice'), function(){
                
                    console.log("Doing")
                    frappe.db.set_value("Payment Entry", frm.doc.name, 'custom_company_abbr', 'VFu')
                    console.log("Done")   
                
                
            }, __("Actions"));
        }
    },
    mode_of_payment(frm){
        if(frm.doc.mode_of_payment){
            frappe.call({
                method: 'upande_vf_custom.custom_scripts.server_scripts.payment_entry.get_reference_no',
                args: {
                    message: {
                        doc: frm.doc
                    }
                },
                btn: $('.primary-action'),
                freeze: true,
                callback: (r) => {
                    if(r.message){
                        console.log(r.message)
                        frm.doc.reference_no = r.message
                        
                        frm.refresh_field("reference_no")
                        frm.save()
                    }
                    
                }
            })
        }
    },
	party(frm) {
	    if(frm.doc.party_type == "Supplier"){
	       frappe.call({
                method: 'upande_vf_custom.custom_scripts.server_scripts.payment_entry.get_supplier_details',
                args: {
                    message: {
                        party: frm.doc.party
                    }
                },
                btn: $('.primary-action'),
                freeze: true,
                callback: (r) => {
                    if (r.message) {
                        let data = r.message
                        
                        if(data.contact){
                            frm.doc.contact_person = data.contact
                        }
                            
                        if(data.email){
                            frm.doc.contact_email = data.email
                        }
                            
                        if(data.bank_acc){
                            frm.doc.party_bank_account = data.bank_acc
                        }
                        
                        frm.refresh_field("contact_person")
                        frm.refresh_field("contact_email")
                        frm.refresh_field("party_bank_account")
    
                        // processDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                        
                    } else {
                        console.log("No message received");
                    }
                },
                error: (r) => {
                    console.error("Error", r);
                    // Handle the error here
                }
            })

	    }
	},
	before_save(frm){
	    if(!frm.doc.party_bank_account){    
	        if(frm.doc.party_type == "Supplier"){
    	        frappe.call({
                    method: 'upande_vf_custom.custom_scripts.server_scripts.payment_entry.get_supplier_details',
                    args: {
                        message: {
                            party: frm.doc.party
                        }
                    },
                    btn: $('.primary-action'),
                    freeze: true,
                    callback: (r) => {
                        if (r.message) {
                            let data = r.message
                            
                            if(data.contact){
                                frm.doc.contact_person = data.contact
                            }
                                
                            if(data.email){
                                frm.doc.contact_email = data.email
                            }
                                
                            if(data.bank_acc){
                                frm.doc.party_bank_account = data.bank_acc
                            }
                            
                            frm.refresh_field("contact_person")
                            frm.refresh_field("contact_email")
                            frm.refresh_field("party_bank_account")
                            
                            // frm.save()
        
                            // processDraftPayments(frm, r.message.draft_payments, r.message.total_grand_total);
                            
                        } else {
                            console.log("No message received");
                        }
                    },
                    error: (r) => {
                        console.error("Error", r);
                        // Handle the error here
                    }
                })
	        }
	    }
	}
})