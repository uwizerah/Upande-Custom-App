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
    pack_to_crates(frm){
        frappe.call({
            method: 'updated_child_table',
            doc: frm.doc,
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                let response = r.message
                console.log(response)
                refresh_field("crates")
            }
        })
    }
})
