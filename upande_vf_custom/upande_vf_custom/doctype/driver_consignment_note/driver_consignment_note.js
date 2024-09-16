// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Driver Consignment Note', {
	refresh(frm){
	    if(frm.doc.docstatus==1){
	        frm.add_custom_button(__('Delivery Note'), function(){
            frappe.call({
                method: 'create_delivery_note',
                doc: frm.doc,
                btn: $('.primary-action'),
                freeze: true,
                callback: (r) => {
                    let response = r.message
                    var name = response.name;
                    
                    frappe.set_route('Form', 'Delivery Note', name);
                }
            })
            
            }, __("Create"));
	    }
    },
    items(frm){
        console.log("items")
    }
})

frappe.ui.form.on('Consignment Note Item', {
    qty(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
        let row = frappe.get_doc(cdt, cdn);
        
        frappe.call({
            method: 'updated_child_table',
            doc: frm.doc,
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                let response = r.message
                console.log(response)
                
            }
        })
        

    }
})

frappe.ui.form.on('Order Break Down', {
    crates_delete(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
        let row = frappe.get_doc(cdt, cdn);
        
        // if (frm.doc.default_account_paid_to) {
        //     frappe.model.set_value(cdt, cdn, 'account_paid_to', frm.doc.default_account_paid_to);
        // }
        
        // set_mode_of_payment(frm, cdt, cdn, row.account_paid_from, frm.doc.company);

        console.log('A row has been deleted to the links table 🎉');
    }
})