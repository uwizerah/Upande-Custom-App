frappe.ui.form.on('Sales Order', {
    onload(frm){
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__('Consignment Note'), function(){
                
                // frappe.call({
                //         method: 'upande_vf_custom.custom_scripts.server_scripts.purchase_invoice.update_taxes',
                //         args: {
                //             message: {
                //                 doc_name: frm.doc.name
                //             }
                //         },
                //         btn: $('.primary-action'),
                //         freeze: true,
                //         callback: (r) => {
                //             // if(r.message){
                //             //     console.log(r.message)
                //             //     frm.doc.reference_no = r.message
                //                 console.log(frm.doc.taxes)
                //                 frm.refresh_field("taxes")
                //                 // frm.save()
                //             // }
                            
                //         }
                //     })
                    // frappe.db.set_value("Payment Entry", frm.doc.name, 'custom_remittance_sent', 1)
                
                
            }, __("Create"));
        }
    },
    // after_save(frm){
    //     frappe.call({
    //         method: 'upande_vf_custom.custom_scripts.server_scripts.purchase_invoice.update_taxes',
    //         args: {
    //             message: {
    //                 doc_name: frm.doc.name
    //             }
    //         },
    //         btn: $('.primary-action'),
    //         freeze: true,
    //         callback: (r) => {
    //             // if(r.message){
    //             //     console.log(r.message)
    //             //     frm.doc.reference_no = r.message
    //                 console.log(frm.doc.taxes)
    //                 frm.refresh_field("taxes")
    //                 // frm.save()
    //             // }
                
    //         }
    //     })
    
    // }
})

